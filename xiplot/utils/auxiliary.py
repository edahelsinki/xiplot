from typing import Optional, Union

import pandas as pd

CLUSTER_COLUMN_NAME = "Xiplot_cluster"
SELECTED_COLUMN_NAME = "Xiplot_selected"


def get_clusters(aux: pd.DataFrame, n: Optional[int] = None) -> pd.Categorical:
    """Get the cluster column from the auxiliary data.

    Args:
        aux: Auxiliary data frame.
        n: Column size if missing. Defaults to `aux.shape[0]`.

    Returns:
        Categorical column with clusters (creates a column with `n` "all" if missing)
    """
    if not isinstance(aux, pd.DataFrame):
        aux = decode_aux(aux)
    if CLUSTER_COLUMN_NAME in aux:
        return pd.Categorical(aux[CLUSTER_COLUMN_NAME].copy())
    if n is None:
        n = aux.shape[0]
    return pd.Categorical(["all"]).repeat(n)


def get_selected(aux: pd.DataFrame, n: Optional[int] = None) -> pd.Series:
    """Get the selected column from the auxiliary data.

    Args:
        aux: Auxiliary data frame.
        n: Column size if missing. Defaults to `aux.shape[0]`.

    Returns:
        Column with booleans (creates a column with `[False] * n` if missing)
    """
    if not isinstance(aux, pd.DataFrame):
        aux = decode_aux(aux)
    if SELECTED_COLUMN_NAME in aux:
        return aux[SELECTED_COLUMN_NAME].copy()
    if n is None:
        n = aux.shape[0]
    return pd.Series([False]).repeat(n).reset_index(drop=True)


def decode_aux(aux: str) -> pd.DataFrame:
    if isinstance(aux, pd.DataFrame):
        return aux
    return pd.read_json(aux, orient="table")


def encode_aux(aux: pd.DataFrame) -> str:
    return aux.to_json(orient="table", index=False)


def merge_df_aux(
    df: pd.DataFrame, aux: Union[str, pd.DataFrame]
) -> pd.DataFrame:
    if not isinstance(aux, pd.DataFrame):
        aux = decode_aux(aux)
    aux.index = df.index
    return pd.concat((df, aux), axis=1)
