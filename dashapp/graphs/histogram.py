import numpy as np
import pandas as pd
import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH

from dashapp.utils.layouts import layout_wrapper
from dashapp.graphs import Graph


class Histogram(Graph):
    @staticmethod
    def name() -> str:
        return "Histogram"

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "histogram", "index": MATCH}, "figure"),
            Output({"type": "histogram-container", "index": MATCH}, "style"),
            Input({"type": "x_axis_histo", "index": MATCH}, "value"),
            Input("selection_cluster_dropdown", "value"),
            Input("comparison_cluster_dropdown", "value"),
            State("data_frame_store", "data"),
            State("clusters_column_store", "data"),
            prevent_initial_call=True,
        )
        def render_histogram(x_axis, selection, comparison, df, kmeans_col):
            df = df_from_store(df)
            if kmeans_col:
                if len(kmeans_col) == df.shape[0]:
                    df["Clusters"] = kmeans_col
                fig = make_fig_property(df, x_axis, selection, comparison, kmeans_col)
            else:
                fig = px.histogram(df, x_axis)
            style = {"widthe": "32%", "display": "inline-block", "float": "left"}
            return fig, style

    @staticmethod
    def create_new_layout(index, df, columns):
        return html.Div(
            [
                dcc.Graph(
                    id={"type": "histogram", "index": index},
                    figure=px.histogram(df, columns[0]),
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "x_axis_histo", "index": index},
                        value=columns[0],
                        clearable=False,
                        options=columns,
                    ),
                    title="x axis",
                    style={"margin-top": 10, "margin-left": "10%", "width": "82%"},
                ),
            ],
            id={"type": "histogram-container", "index": index},
            style={"width": "32%", "display": "inline-block", "float": "left"},
        )


def make_fig_property(df, property, cluster, comparison, clusters):
    props_a = []
    props_b = []

    for c, p in zip(clusters, df[property]):
        if c == cluster or cluster == "bg":
            props_a.append(p)

        if c == comparison or comparison == "bg":
            props_b.append(p)

    if cluster == comparison:
        props_b = []

    props = pd.DataFrame(
        {
            "Clusters": [cluster for _ in props_a] + [comparison for _ in props_b],
            property: props_a + props_b,
        }
    )

    fig_property = px.histogram(
        props,
        x=property,
        color="Clusters",
        hover_data={
            "Clusters": False,
            property: False,
        },
        color_discrete_map={
            "bg": px.colors.qualitative.Plotly[0],
            **{f"c{i+1}": c for i, c in enumerate(px.colors.qualitative.Plotly[1:])},
        },
        opacity=0.75,
        histnorm="probability density",
    )

    fig_property.update_layout(
        hovermode="x unified",
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        barmode="overlay",
        yaxis=dict(
            tickformat=".2%",
        ),
    )

    return fig_property
