import warnings

import plotly.express as px

from dash import html, dcc

from dashapp.utils.layouts import layout_wrapper, delete_button
from dashapp.graphs import Graph


class Barplot(Graph):
    @staticmethod
    def name() -> str:
        return "Barplot"

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        warnings.warn("Barplot is unimplemented")

    @staticmethod
    def create_new_layout(index, df, columns):
        return html.Div(
            [
                delete_button("barplot-delete", index),
                dcc.Graph(
                    id={"type": "barplot", "index": index},
                    figure=px.bar(df, columns[6], columns[3]),
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "barplot_x_axis", "index": index},
                        value=columns[0],
                        clearable=False,
                        options=columns,
                    ),
                    title="x axis",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "barplot_y_axis", "index": index},
                        value=columns[1],
                        clearable=False,
                        options=columns,
                    ),
                    title="y axis",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "barplot_cluster_amount", "index": index},
                    ),
                    title="Cluster amount",
                ),
            ],
            id={"type": "histogram-container", "index": index},
            style={"width": "32%", "display": "inline-block", "float": "left"},
        )
