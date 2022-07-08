import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH
import pandas as pd
import numpy as np

from dashapp.services.dash_layouts import layout_wrapper
from dashapp.services.data_frame import get_cluster_centers
from dashapp.graphs import Graph


class Heatmap(Graph):
    @staticmethod
    def name() -> str:
        return "Heatmap"

    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output({"type": "heatmap", "index": MATCH}, "figure"),
            Output({"type": "heatmap-container", "index": MATCH}, "style"),
            Input({"type": "heatmap_cluster_amount", "index": MATCH}, "value"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def render_heatmap(n_clusters, df):
            df = pd.read_json(df, orient="split")
            cluster_centers = get_cluster_centers(df=df, k=n_clusters, random_state=42)
            fig = px.imshow(
                cluster_centers,
                x=df.columns.to_list(),
                y=[str(n + 1) for n in range(n_clusters)],
                color_continuous_scale="RdBu",
                origin="lower",
            )
            style = {"widthe": "32%", "display": "inline-block", "float": "left"}
            return fig, style

    @staticmethod
    def create_new_layout(index, df, columns):
        return html.Div(
            [
                dcc.Graph(
                    id={"type": "heatmap", "index": index},
                    figure=px.imshow(df, color_continuous_scale="RdBu", origin="lower"),
                ),
                layout_wrapper(
                    component=dcc.Slider(
                        min=2,
                        max=10,
                        step=1,
                        id={"type": "heatmap_cluster_amount", "index": index},
                    ),
                    title="Cluster amount",
                    style={"width": "80%"},
                ),
            ],
            id={"type": "heatmap-container", "index": index},
            style={"width": "32%", "display": "inline-block", "float": "left"},
        )
