import pandas as pd
import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH

from dashapp.utils.layouts import layout_wrapper, delete_button, cluster_dropdown
from dashapp.utils.dataframe import get_numeric_columns
from dashapp.graphs import Graph


class Histogram(Graph):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "histogram", "index": MATCH}, "figure"),
            Input({"type": "x_axis_histo", "index": MATCH}, "value"),
            Input({"type": "hg_cluster_comparison_dropdown", "index": MATCH}, "value"),
            Input("clusters_column_store", "data"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def tmp(x_axis, selected_clusters, kmeans_col, df):
            return Histogram.render(
                x_axis, selected_clusters, kmeans_col, df_from_store(df)
            )

    @staticmethod
    def render(x_axis, selected_clusters, kmeans_col, df):
        if len(kmeans_col) == df.shape[0]:
            df["Clusters"] = kmeans_col
        fig = make_fig_property(df, x_axis, selected_clusters, kmeans_col)

        return fig

    @staticmethod
    def create_new_layout(index, df, columns):
        num_columns = get_numeric_columns(df, columns)
        return html.Div(
            [
                delete_button("plot-delete", index),
                dcc.Graph(
                    id={"type": "histogram", "index": index},
                    figure=px.histogram(df, num_columns[0]),
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "x_axis_histo", "index": index},
                        value=num_columns[0],
                        clearable=False,
                        options=num_columns,
                    ),
                    css_class="dd-single",
                    title="x axis",
                ),
                cluster_dropdown(
                    "hg_cluster_comparison_dropdown",
                    index,
                    multi=True,
                    clearable=True,
                    value="all",
                    title="Cluster Comparison",
                    css_class="dd-single",
                ),
            ],
            id={"type": "histogram-container", "index": index},
            className="graphs",
        )


def make_fig_property(df, x_axis, selected_clusters, clusters):
    if not selected_clusters:
        return None
    if type(selected_clusters) == str:
        selected_clusters = [selected_clusters]
    props_dict = {"all": []}
    for s in selected_clusters:
        if s != "all":
            props_dict[s] = []

    for c, p in zip(clusters, df[x_axis]):
        if c != "all" and c in selected_clusters:
            props_dict[c].append(p)
        props_dict["all"].append(p)

    clusters_col = []
    x = []
    for s in selected_clusters:
        clusters_col += [s for _ in props_dict[s]]
        x += props_dict[s]

    dff = pd.DataFrame({"Clusters": clusters_col, x_axis: x})

    fig_property = px.histogram(
        dff,
        x=x_axis,
        color="Clusters",
        hover_data={
            "Clusters": False,
            x_axis: False,
        },
        color_discrete_map={
            "all": px.colors.qualitative.Plotly[0],
            **{f"c{i+1}": c for i, c in enumerate(px.colors.qualitative.Plotly[1:])},
        },
        opacity=0.5,
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
