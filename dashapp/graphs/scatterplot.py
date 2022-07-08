import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH
import pandas as pd
import numpy as np

from dashapp.services.dash_layouts import layout_wrapper
from dashapp.graphs import Graph


class Scatterplot(Graph):
    @staticmethod
    def name() -> str:
        return "Scatterplot"

    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output({"type": "scatterplot", "index": MATCH}, "figure"),
            Output({"type": "scatterplot-container", "index": MATCH}, "style"),
            Output({"type": "jitter-slider", "index": MATCH}, "max"),
            Output({"type": "scatter_x_axis", "index": MATCH}, "options"),
            Output({"type": "scatter_y_axis", "index": MATCH}, "options"),
            Output({"type": "scatter_target_color", "index": MATCH}, "options"),
            Output({"type": "scatter_target_symbol", "index": MATCH}, "options"),
            Input({"type": "scatter_x_axis", "index": MATCH}, "value"),
            Input({"type": "scatter_y_axis", "index": MATCH}, "value"),
            Input({"type": "scatter_target_color", "index": MATCH}, "value"),
            Input({"type": "scatter_target_symbol", "index": MATCH}, "value"),
            Input({"type": "jitter-slider", "index": MATCH}, "value"),
            Input("clusters_column_store", "data"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def render_scatterplot(x_axis, y_axis, color, symbol, jitter, kmeans_col, df):
            df = pd.read_json(df, orient="split")

            if kmeans_col:
                if len(kmeans_col) == df.shape[0]:
                    df["Clusters"] = kmeans_col
            columns = df.columns.to_list()

            jitter_max = (df[x_axis].max() - df[x_axis].min()) * 0.05
            if jitter:
                jitter = float(jitter)
            if type(jitter) == float:
                if jitter > 0:
                    Z = df[[x_axis, y_axis]].to_numpy("float64")
                    Z = np.random.normal(Z, jitter)
                    jitter_df = pd.DataFrame(Z, columns=[x_axis, y_axis])
                    df[[x_axis, y_axis]] = jitter_df[[x_axis, y_axis]]

            fig = px.scatter(
                data_frame=df,
                x=x_axis,
                y=y_axis,
                color=color,
                symbol=symbol,
                color_discrete_map={
                    "bg": px.colors.qualitative.Plotly[0],
                    **{
                        f"c{i+1}": c
                        for i, c in enumerate(px.colors.qualitative.Plotly[1:])
                    },
                    "*": "#000000",
                },
                custom_data=["auxiliary"],
            )
            fig.update_layout(showlegend=False)
            fig.update(layout_coloraxis_showscale=False)

            style = {"width": "32%", "display": "inline-block", "float": "left"}

            return fig, style, jitter_max, columns, columns, columns, columns

    @staticmethod
    def create_new_layout(index, df, columns):
        return html.Div(
            children=[
                dcc.Graph(
                    id={"type": "scatterplot", "index": index},
                    figure=px.scatter(df, columns[0], columns[1]),
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_x_axis", "index": index},
                        options=columns,
                        value=columns[0],
                        clearable=False,
                    ),
                    title="x",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_y_axis", "index": index},
                        options=columns,
                        value=columns[1],
                        clearable=False,
                    ),
                    title="y",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_target_color", "index": index},
                        options=columns,
                    ),
                    title="target (color)",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_target_symbol", "index": index},
                        options=columns,
                    ),
                    title="target (symbol)",
                ),
                layout_wrapper(
                    component=dcc.Slider(
                        id={"type": "jitter-slider", "index": index},
                        min=0,
                        max=1,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                    title="jitter",
                    style={"width": "80%", "padding-left": "2%"},
                ),
            ],
            id={"type": "scatterplot-container", "index": index},
            style={"width": "32%", "display": "inline-block", "float": "left"},
        )
