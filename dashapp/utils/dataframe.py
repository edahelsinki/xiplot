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
        if tarfile.is_tarfile(data):
            stem = Path(filename).name[: -len("".join(Path(filename).suffixes))]

            with tarfile.open(data, "r:*") as tar:
                dfname = None
                metaname = None

                for name in tar.getnames():
                    if Path(name).stem == stem:
                        if Path(name).suffix in [".csv", ".json", ".pkl", ".ft"]:
                            if dfname is not None:
                                return None
                            dfname = name
                        elif Path(name).suffix == ".viz":
                            if metaname is not None:
                                return None
                            metaname = name

                if dfname is None or metaname is None:
                    return None

                metadata = json.load(tar.extractfile(metaname)) or dict()
                metadata["filename"] = dfname

                print("Loaded metadata for", filename, metadata)

                return read_only_dataframe(tar.extractfile(dfname), dfname)

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
