import warnings

import plotly.express as px

from dash import html, dcc

from dashapp.services.dash_layouts import layout_wrapper
from dashapp.graphs import Graph


class Barplot(Graph):
    @staticmethod
    def name() -> str:
        return "Barplot"

    @staticmethod
    def register_callbacks(app):
        warnings.warn("Barplot is unimplemented")

    @staticmethod
    def create_new_layout(index, df, columns):
        return html.Div(
            [
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
