import json
import tarfile
from collections import OrderedDict
from io import BytesIO
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
)

import pandas as pd

from xiplot.tabs.plugins import get_plugins_cached
from xiplot.utils.io import FinallyCloseBytesIO


def get_data_filepaths(data_dir=""):
    try:
        return sorted(
            (fp for fp in Path(data_dir).iterdir() if fp.is_file()),
            reverse=True,
        )

    except FileNotFoundError:
        return []


def read_functions() -> (
    Iterator[Tuple[Callable[[BytesIO], pd.DataFrame], str]]
):
    """Generate all functions for reading to a dataframe.

    Yields:
        fn: Function that reads the data and returns a dataframe.
        ext: File extension that the readed can handle.
    """
    for _, _, plugin in get_plugins_cached("read"):
        plugin = plugin()
        if plugin is not None:
            yield plugin

    def read_json(data):
        if isinstance(data, BytesIO):
            data = data.getvalue().decode("utf-8")
        elif isinstance(data, tarfile.ExFileObject):
            data = data.read().decode("utf-8")

        try:
            return pd.read_json(data, typ="frame", orient="columns")
        except Exception:
            return pd.read_json(data, typ="frame", orient="split")

    yield pd.read_csv, ".csv"
    yield read_json, ".json"


def write_functions() -> (
    Iterator[Tuple[Callable[[pd.DataFrame, BytesIO], None], str, str]]
):
    """Generate all functions for writing dataframes.

    Yields:
        fn: Function that writes the dataframe to bytes.
        ext: File extension that matches the written data.
        mime: MIME type of the written data.
    """
    for _, _, plugin in get_plugins_cached("write"):
        plugin = plugin()
        if plugin is not None:
            yield plugin

    yield lambda df, file: df.to_csv(file, index=False), ".csv", "text/csv"
    yield lambda df, file: df.to_json(
        file, orient="split", index=False
    ), ".json", "application/json"


def read_dataframe_with_extension(data, filename=None):
    """
    Read the given data and convert it to a pandas data frame

    Parameters:

        data: File name or File-like object
        filename: File name as a string

    Returns:

        df: Pandas data frame
        aux: Pandas data frame
        meta: dictionary of metadata
    """
    if filename is None:
        filename = data

    if ".tar" in Path(filename).suffixes:
        stem = Path(filename).name[: -len("".join(Path(filename).suffixes))]

        with (
            tarfile.open(name=data)
            if isinstance(data, (str, Path))
            else tarfile.open(fileobj=data)
        ) as tar:
            df_file = None
            df_name = None
            aux_file = None
            aux_name = None
            meta_file = None

            for member in tar.getmembers():
                if not member.isfile():
                    raise Exception(
                        f"Tar contains a non-file entry {member.name}"
                    )

                if Path(member.name).stem == "data":
                    if df_file is not None:
                        raise Exception("Tar contains more than one data file")
                    df_file = tar.extractfile(member)
                    df_name = Path(stem).with_suffix(Path(member.name).suffix)
                elif Path(member.name).stem == "aux":
                    if aux_file is not None:
                        raise Exception(
                            "Tar contains more than one auxiliary file"
                        )
                    aux_file = tar.extractfile(member)
                    aux_name = member.name
                elif member.name == "meta.json":
                    if meta_file is not None:
                        raise Exception("Tar contains more than metadata file")
                    meta_file = tar.extractfile(member)
                else:
                    raise Exception(
                        f"Tar contains extraneous file '{member.name}'"
                    )

            if df_file is None:
                raise Exception("Tar contains no data file called 'data.*'")

            if aux_file is None:
                raise Exception(
                    "Tar contains no auxiliary file called 'aux.*'"
                )

            if meta_file is None:
                raise Exception(
                    "Tar contains no metadata file called 'meta.json'"
                )

            metadata = (
                json.load(meta_file, object_pairs_hook=OrderedDict)
                or OrderedDict()
            )
            metadata["filename"] = str(df_name)

            df = read_only_dataframe(df_file, df_name)

            try:
                aux = read_only_dataframe(aux_file, aux_name)
            except pd.errors.EmptyDataError:
                aux = pd.DataFrame()

            if aux.empty:
                aux.index = df.index
            if df.shape[0] != aux.shape[0]:
                raise Exception(
                    "The dataframe and auxiliary data have different number of"
                    " rows."
                )

            return df, aux, metadata

    df = read_only_dataframe(data, filename)
    return (
        df,
        pd.DataFrame(index=df.index),
        OrderedDict(filename=str(filename)),
    )


def read_only_dataframe(data, filename):
    file_extension = Path(filename).suffix
    error = None

    for fn, ext in read_functions():
        if file_extension == ext:
            try:
                return fn(data)
            except Exception as e:
                error = e

    if error is not None:
        raise error
    raise Exception(f"Unsupported dataframe format '{file_extension}'")


def write_dataframe_and_metadata(
    df: pd.DataFrame,
    aux: pd.DataFrame,
    meta: Dict[str, Any],
    filepath: str,
    file,
    file_extension: Optional[str] = None,
) -> Tuple[str, str]:
    if not aux.empty and df.shape[0] != aux.shape[0]:
        raise Exception(
            "The dataframe and auxiliary data have different number of rows."
        )
    if file_extension is None:
        file_extension = Path(filepath).suffix

    with tarfile.open(fileobj=file, mode="w:gz") as tar:
        df_file = Path("data").with_suffix(file_extension).name
        aux_file = Path("aux").with_suffix(file_extension).name
        meta_file = "meta.json"
        tar_file = Path(filepath).with_suffix(".tar.gz").name

        with FinallyCloseBytesIO() as df_bytes:
            write_only_dataframe(df, filepath, df_bytes, file_extension)
            df_bytes = df_bytes.getvalue()

        df_info = tarfile.TarInfo(df_file)
        df_info.size = len(df_bytes)

        tar.addfile(df_info, BytesIO(df_bytes))

        with FinallyCloseBytesIO() as aux_bytes:
            write_only_dataframe(aux, aux_file, aux_bytes, file_extension)
            aux_bytes = aux_bytes.getvalue()

        aux_info = tarfile.TarInfo(aux_file)
        aux_info.size = len(aux_bytes)

        tar.addfile(aux_info, BytesIO(aux_bytes))

        meta = meta or OrderedDict()
        meta["filename"] = Path(filepath).name

        meta_string = json.dumps(meta)
        meta_bytes = meta_string.encode("utf-8")

        meta_info = tarfile.TarInfo(meta_file)
        meta_info.size = len(meta_bytes)

        tar.addfile(meta_info, BytesIO(meta_bytes))

        return tar_file, "application/gzip"


def write_only_dataframe(
    df: pd.DataFrame,
    filepath: str,
    file: BytesIO,
    file_extension: Optional[str] = None,
) -> Tuple[str, str]:
    if file_extension is None:
        file_name = Path(filepath).name
        file_extension = Path(filepath).suffix
    else:
        file_name = Path(filepath).with_suffix(file_extension).name
    error = None

    for fn, ext, mime in write_functions():
        if file_extension == ext:
            try:
                fn(df, file)
                return file_name, mime
            except Exception as e:
                error = e

    if error is not None:
        raise error
    raise Exception(f"Unsupported dataframe format '{file_extension}'")


def get_numeric_columns(df, columns=None):
    """
    Return only columns, which are numeric

    Parameters:
        df: pandas.DataFrame
        columns: columns of the data frame

    Returns:
        columns: numeric columns
    """
    if columns is not None:
        df = df[columns]
    return df.select_dtypes("number").columns.to_list()


def get_default_column(
    columns: List[str], axis: Literal["x", "y"]
) -> Optional[str]:
    """Get default values for x_axis and y_axis from a list of column names.

    Args:
        columns: List of column names.
        axis: Is this the "x" or "y" axis.

    Returns:
        Column name.
    """
    if len(columns) == 0:
        return None
    if axis == "x":
        for c in columns:
            if "x" in c or "1" in c or "X" in c:
                return c
        return columns[0]

    else:
        for c in columns:
            if "y" in c or "2" in c or "Y" in c:
                return c
        return columns[min(1, len(columns) - 1)]
