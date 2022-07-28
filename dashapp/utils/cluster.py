import plotly.express as px


def cluster_colours():
    return {
        "all": px.colors.qualitative.Plotly[0],
        **{f"c{i+1}": c for i, c in enumerate(px.colors.qualitative.Plotly[1:])},
    }
