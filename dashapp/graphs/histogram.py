import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH
import pandas as pd
import numpy as np

from dashapp.services.dash_layouts import layout_wrapper
from dashapp.graphs import Graph


class Histogram(Graph):
    @staticmethod
    def name() -> str:
        return "Histogram"

    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output({"type": "histogram", "index": MATCH}, "figure"),
            Output({"type": "histogram-container", "index": MATCH}, "style"),
            Input({"type": "x_axis_histo", "index": MATCH}, "value"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def render_histogram(x_axis, df):
            df = pd.read_json(df, orient="split")
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
