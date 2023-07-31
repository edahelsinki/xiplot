from io import BytesIO

import pandas as pd


def read_parquet():
    try:
        df = pd.DataFrame()
        pq = df.to_parquet()
        pd.read_parquet(BytesIO(pq))
    except ImportError:
        return

    return pd.read_parquet, ".parquet"


def write_parquet():
    try:
        pd.DataFrame().to_parquet()
    except ImportError:
        return

    return pd.DataFrame.to_parquet, ".parquet", "application/octet-stream"


def read_feather():
    try:
        df = pd.DataFrame()
        ft = BytesIO()
        df.reset_index().to_feather(ft)
        pd.read_feather(ft)
    except ImportError:
        return

    return pd.read_feather, ".feather"


def write_feather():
    try:
        pd.DataFrame().reset_index().to_feather(BytesIO())
    except ImportError:
        return

    return pd.DataFrame.to_feather, ".feather", "application/octet-stream"
