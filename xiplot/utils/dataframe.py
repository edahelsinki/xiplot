import json
import tarfile
from typing import Any, Dict

import pandas as pd
import numpy as np

from collections import OrderedDict
from io import BytesIO, StringIO
from pathlib import Path

from xiplot.plugin import get_plugins_cached


def get_data_filepaths():
    return sorted((fp for fp in Path("data").iterdir() if fp.is_file()), reverse=True)


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
                    raise Exception(f"Tar contains a non-file entry {member.name}")

                if Path(member.name).stem == "data":
                    if df_file is not None:
                        raise Exception("Tar contains more than one data file")
                    df_file = tar.extractfile(member)
                    df_name = Path(stem).with_suffix(Path(member.name).suffix)
                elif Path(member.name).stem == "aux":
                    if aux_file is not None:
                        raise Exception("Tar contains more than one auxiliary file")
                    aux_file = tar.extractfile(member)
                    aux_name = member.name
                elif member.name == "meta.json":
                    if meta_file is not None:
                        raise Exception("Tar contains more than metadata file")
                    meta_file = tar.extractfile(member)
                else:
                    raise Exception(f"Tar contains extraneous file '{member.name}'")

            if df_file is None:
                raise Exception(f"Tar contains no data file called 'data.*'")

            if aux_file is None:
                raise Exception(f"Tar contains no auxiliary file called 'aux.*'")

            if meta_file is None:
                raise Exception(f"Tar contains no metadata file called 'meta.json'")

            metadata = (
                json.load(meta_file, object_pairs_hook=OrderedDict) or OrderedDict()
            )
            metadata["filename"] = str(df_name)

            df = read_only_dataframe(df_file, df_name)

            try:
                aux = read_only_dataframe(aux_file, aux_name)
            except pd.errors.EmptyDataError:
                aux = pd.DataFrame(dict())

            if not aux.empty and df.shape[0] != aux.shape[0]:
                raise Exception(
                    f"The dataframe and auxiliary data have different number of rows."
                )

            return df, aux, metadata

    return (
        read_only_dataframe(data, filename),
        pd.DataFrame(dict()),
        OrderedDict(filename=str(filename)),
    )


def read_only_dataframe(data, filename):
    file_extension = Path(filename).suffix

    for plugin_read_function, plugin_file_extension in load_plugins_read():

        if file_extension == plugin_file_extension:
            return plugin_read_function(data)

    if file_extension == ".csv":
        return pd.read_csv(data)

    if file_extension == ".json":
        if isinstance(data, BytesIO):
            data = data.getvalue().decode("utf-8")
        elif isinstance(data, tarfile.ExFileObject):
            data = data.read().decode("utf-8")

        try:
            return pd.read_json(data, typ="frame", orient="columns")
        except Exception:
            return pd.read_json(data, typ="frame", orient="split")

    if file_extension == ".ft":
        try:
            return pd.read_feather(data)
        except ImportError:
            pass

    raise Exception(f"Unsupported dataframe format '{file_extension}'")


def load_plugins_read():
    try:
        return load_plugins_read.output
    except AttributeError:
        load_plugins_read.output = [plugin() for plugin in get_plugins_cached("read")]
    return load_plugins_read.output


def write_dataframe_and_metadata(
    df: pd.DataFrame, aux: pd.DataFrame, meta: Dict[str, Any], filepath: str, file
):
    if not aux.empty and df.shape[0] != aux.shape[0]:
        raise Exception(
            f"The dataframe and auxiliary data have different number of rows."
        )

    with tarfile.open(fileobj=file, mode="w:gz") as tar:
        df_file = Path("data").with_suffix(Path(filepath).suffix).name
        aux_file = "aux.json"
        meta_file = "meta.json"
        tar_file = Path(filepath).with_suffix(".tar.gz").name

        df_bytes = BytesIO()
        _, df_mime = write_only_dataframe(df, filepath, df_bytes)
        df_bytes = df_bytes.getvalue()

        df_info = tarfile.TarInfo(df_file)
        df_info.size = len(df_bytes)

        tar.addfile(df_info, BytesIO(df_bytes))

        aux_bytes = BytesIO()
        _, aux_mime = write_only_dataframe(aux, aux_file, aux_bytes)
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


def write_only_dataframe(df, filepath, file):
    file_name = Path(filepath).name
    file_extension = Path(filepath).suffix

    if file_extension == ".csv":
        df.to_csv(file, index=False)
        return file_name, "text/csv"

    if file_extension == ".json":
        df.to_json(file, orient="split", index=False)
        return file_name, "application/json"

    if file_extension == ".ft":
        try:
            df.to_feather(file)
            return file_name, "application/octet-stream"
        except ImportError:
            pass

    # TODO What about plugin supported formats?
    # TODO or maybe we could allow exporting in different formats
    raise Exception(f"Unsupported dataframe format '{file_extension}'")


def get_numeric_columns(df, columns):
    """
    Return only columns, which are numeric

    Parameters:

        df: pandas.DataFrame
        columns: columns of the data frame

    Returns:

        columns: numeric columns
    """
    columns = [
        c
        for c in columns
        if df[c].dtype in (int, float, np.int32, np.int64, np.float32, np.float64)
    ]
    return columns


def get_smiles_column_name(df):
    """
    Return name of smiles column, if it exists

    Parameters:

        df: pandas.DataFrame

    Returns:

        smiles_col: name of smiles column(str) / returns None, if it's not found
    """
    smiles_col = None
    for s in ["SMILES", "smiles", "Smiles"]:
        if s in df.columns:
            smiles_col = s

    return smiles_col
