import pandas as pd
import plotly.express as px


CLUSTER_COLUMN_NAME = "Xiplot_cluster"
SELECTED_COLUMN_NAME = "Xiplot_selected"


def get_clusters(aux: pd.DataFrame, n: int = -1) -> pd.Categorical:
    """Get the cluster column from the auxiliary data.

    Args:
        aux: Auxiliary data frame.
        n: Column size if missing. Defaults to `aux.shape[0]`.

    Returns:
        Categorical column with clusters (creates a column with `n` "all" if missing)
    """
    if CLUSTER_COLUMN_NAME in aux:
        return pd.Categorical(aux[CLUSTER_COLUMN_NAME])
    if n == -1:
        n = aux.shape[0]
    return pd.Categorical(["all"]).repeat(n)


def get_selected(aux: pd.DataFrame, n: int = -1) -> pd.Series:
    """Get the selected column from the auxiliary data.

    Args:
        aux: Auxiliary data frame.
        n: Column size if missing. Defaults to `aux.shape[0]`.

    Returns:
        Column with booleans (creates a column with `[False] * n` if missing)
    """
    if SELECTED_COLUMN_NAME in aux:
        return aux[SELECTED_COLUMN_NAME]
    if n == -1:
        n = aux.shape[0]
    return pd.Series([False]).repeat(n).reset_index(drop=True)


def cluster_colours():
    return {
        "all": px.colors.qualitative.Vivid[-1],
        **{
            f"c{i+1}": c
            for i, c in enumerate(px.colors.qualitative.Vivid[:-1])
        },
    }


def KMeans(n_clusters: int = 8, **kwargs) -> object:
    """A wrapper around `sklearn.cluster.KMeans` that changes `n_init="warn"`
    to `n_init="auto"`. This is needed to avoid a warning for scikit-learn
    versions `>=1.2,<1.4`. Older and newer versions are not affected (unless
    `n_init="warn"` is manually specified).

    NOTE: This function lazily loads scikit-learn (so the first call might be
     slow).

    Args:
        n_clusters: The number of clusters. Defaults to 8.
        **kwargs: See `sklearn.cluster.KMeans`.

    Returns:
        An instance of `sklearn.cluster.KMeans`.
    """
    from sklearn.cluster import KMeans

    km = KMeans(n_clusters, **kwargs)
    if km.n_init == "warn":
        km.n_init == "auto"
    return km
