import pandas as pd

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
