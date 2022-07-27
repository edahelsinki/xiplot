import json
import tarfile

import pandas as pd
import numpy as np

from pathlib import Path


def get_data_filepaths():
    return [fp for fp in Path("data").iterdir() if fp.is_file()]


def read_dataframe_with_extension(data, filename=None):
    """
    Read the given data and convert it to a pandas data frame

    Parameters
    ----------
        data: File name or File-like object
        filename: File name as a string

    Returns
    -------
        df: Pandas data frame
    """
    if filename is None:
        filename = data

    try:
        if ".tar" in Path(filename).suffixes:
            stem = Path(filename).name[: -len("".join(Path(filename).suffixes))]

            with (
                tarfile.open(name=data)
                if isinstance(data, (str, Path))
                else tarfile.open(fileobj=data)
            ) as tar:
                df_file = None
                df_name = None
                meta_file = None

                for member in tar.getmembers():
                    if not member.isfile():
                        continue

                    if Path(member.name).stem != stem:
                        continue

                    if Path(member.name).suffix in [".csv", ".json", ".pkl", ".ft"]:
                        if df_file is not None:
                            return None
                        df_file = tar.extractfile(member)
                        df_name = member.name
                    elif Path(member.name).suffix == ".viz":
                        if meta_file is not None:
                            return None
                        meta_file = tar.extractfile(member)

                if df_file is None or meta_file is None:
                    return None

                metadata = json.load(meta_file) or dict()
                metadata["filename"] = df_name

                print("Loaded metadata for", filename, metadata)

                return read_only_dataframe(df_file, df_name)

        return read_only_dataframe(data, filename)
    except Exception as err:
        print(err)

        return None


def read_only_dataframe(data, filename):
    file_extension = Path(filename).suffix

    if file_extension == ".csv":
        return pd.read_csv(data)

    if file_extension == ".json":
        return pd.read_json(data)

    if file_extension == ".pkl":
        return pd.read_pickle(data)

    if file_extension == ".ft":
        try:
            return pd.read_feather(data)
        except ImportError:
            return None

    return None


def get_numeric_columns(df, columns):
    columns = [
        c
        for c in columns
        if type(df[c][0]) in (int, float, np.int32, np.int64, np.float32, np.float64)
    ]
    return columns
