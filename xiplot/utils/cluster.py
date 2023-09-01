import plotly.express as px


def cluster_colours():
    return {
        "all": px.colors.qualitative.Vivid[-1],
        **{
            f"c{i+1}": c
            for i, c in enumerate(px.colors.qualitative.Vivid[:-1])
        },
    }


def KMeans(n_clusters: int = 8, **kwargs):
    """A wrapper around `sklearn.cluster.KMeans` that changes `n_init="warn"`
    to `n_init="auto"`. This is needed to avoid a warning for scikit-learn
    versions `>=1.2,<1.4`. Older and newer versions are not affected (unless
    `n_init="warn"` is manually specified).

    NOTE: This function lazily loads scikit-learn (so the first call might be slow).

    Args:
        n_clusters: The number of clusters. Defaults to 8.
        **kwargs: See `sklearn.cluster.KMeans`.

    Returns:
        An instance of `sklearn.cluster.KMeans`.
    """
    from sklearn.cluster import KMeans

    km = KMeans(n_clusters, **kwargs)
    if km.n_init == "warn":
        km.n_init = "auto"
    return km
