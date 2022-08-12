import json

import numpy as np
import pandas as pd
import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import layout_wrapper, delete_button
from dashapp.utils.dataframe import get_numeric_columns
from dashapp.utils.cluster import cluster_colours
from dashapp.utils.scatterplot import get_row
from dashapp.plots import Plot


class Scatterplot(Plot):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "scatterplot", "index": MATCH}, "figure"),
            Output({"type": "jitter-slider", "index": MATCH}, "max"),
            Input({"type": "scatter_x_axis", "index": MATCH}, "value"),
            Input({"type": "scatter_y_axis", "index": MATCH}, "value"),
            Input({"type": "scatter_target_color", "index": MATCH}, "value"),
            Input({"type": "scatter_target_symbol", "index": MATCH}, "value"),
            Input({"type": "jitter-slider", "index": MATCH}, "value"),
            Input("selected_rows_store", "data"),
            Input("clusters_column_store", "data"),
            Input("data_frame_store", "data"),
        )
        def tmp(x_axis, y_axis, color, symbol, jitter, selected_rows, kmeans_col, df):
            if ctx.triggered_id == "data_frame_store":
                raise PreventUpdate()

            jitter_max = (df[x_axis].max() - df[x_axis].min()) * 0.05
            return (
                Scatterplot.render(
                    df_from_store(df),
                    x_axis,
                    y_axis,
                    color,
                    symbol,
                    jitter,
                    selected_rows,
                    kmeans_col,
                ),
                jitter_max,
            )

        @app.callback(
            output=dict(
                selected_rows_store=Output("selected_rows_store", "data"),
                click_store=Output("lastly_clicked_point_store", "data"),
                scatter=Output({"type": "scatterplot", "index": ALL}, "clickData"),
            ),
            inputs=[
                Input({"type": "scatterplot", "index": ALL}, "clickData"),
                State("selected_rows_store", "data"),
            ],
        )
        def handle_click_events(click, selected_rows):
            if ctx.triggered_id is None:
                raise PreventUpdate()

            if not selected_rows:
                selected_rows = []

            row = get_row(click)
            if row is None:
                raise PreventUpdate()

            if not selected_rows[row]:
                selected_rows[row] = True
            else:
                selected_rows[row] = False

            scatter_amount = len(ctx.outputs_grouping["scatter"])

            return dict(
                selected_rows_store=selected_rows,
                click_store=row,
                scatter=[None] * scatter_amount,
            )

        @app.callback(
            output=dict(
                hover_store=Output("lastly_hovered_point_store", "data"),
                scatter=Output({"type": "scatterplot", "index": ALL}, "hoverData"),
            ),
            inputs=[
                Input({"type": "scatterplot", "index": ALL}, "hoverData"),
            ],
        )
        def handle_hover_events(hover):
            row = get_row(hover)
            if row is None:
                raise PreventUpdate()

            scatter_amount = len(ctx.outputs_grouping["scatter"])
            return dict(
                hover_store=row,
                scatter=[None] * scatter_amount,
            )

    @staticmethod
    def render(
        df,
        x_axis,
        y_axis,
        color=None,
        symbol=None,
        jitter=None,
        selected_rows=None,
        kmeans_col=[],
    ):
        if len(kmeans_col) == df.shape[0]:
            df["Clusters"] = kmeans_col
        else:
            df["Clusters"] = ["all"] * df.shape[0]

        if jitter:
            jitter = float(jitter)
        if type(jitter) == float:
            if jitter > 0:
                Z = df[[x_axis, y_axis]].to_numpy("float64")
                Z = np.random.normal(Z, jitter)
                jitter_df = pd.DataFrame(Z, columns=[x_axis, y_axis])
                df[["jitter-x", "jitter-y"]] = jitter_df[[x_axis, y_axis]]
                x_axis, y_axis = "jitter-x", "jitter-y"
        sizes = [0.5] * df.shape[0]
        colors = df.copy().loc[:, color]
        row_ids = []
        id = 0
        if selected_rows:
            for row in selected_rows:
                if not row:
                    row_ids.append(id)
                id += 1
        for id in row_ids:
            sizes[id] = 5
            colors[id] = "*"

        df["__Sizes__"] = sizes
        df["__Color__"] = colors
        df["__Auxiliary__"] = [{"index": i} for i in range(len(df))]

        fig = px.scatter(
            data_frame=df,
            x=x_axis,
            y=y_axis,
            color="__Color__",
            symbol=symbol,
            size="__Sizes__" if 5 in sizes else None,
            opacity=1,
            color_discrete_map={
                "*": "#000000",
                **cluster_colours(),
            },
            custom_data=["__Auxiliary__"],
            hover_data={"__Color__": False, "__Sizes__": False},
            render_mode="webgl",
        )
        fig.update_layout(showlegend=False, uirevision=json.dumps([x_axis, y_axis]))
        fig.update(layout_coloraxis_showscale=False)
        fig.update_traces(marker={"line": {"width": 0}})

        return fig

    @staticmethod
    def create_new_layout(index, df, columns):
        x = None
        y = None
        df["__Auxiliary__"] = [{"index": i} for i in range(len(df))]
        num_columns = get_numeric_columns(df, columns)
        for c in num_columns:
            if "x-" in c or " 1" in c:
                x = c
            elif "y-" in c or " 2" in c:
                y = c
                break
        return html.Div(
            children=[
                delete_button("plot-delete", index),
                dcc.Graph(
                    id={"type": "scatterplot", "index": index},
                    figure=px.scatter(
                        df,
                        x if x else df.columns[0],
                        y if y else df.columns[1],
                        custom_data=["__Auxiliary__"],
                        render_mode="webgl",
                    ),
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_x_axis", "index": index},
                        options=num_columns,
                        value=x if x else df.columns[0],
                        clearable=False,
                    ),
                    css_class="dd-double-left",
                    title="x",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_y_axis", "index": index},
                        options=num_columns,
                        value=y if y else df.columns[1],
                        clearable=False,
                    ),
                    css_class="dd-double-right",
                    title="y",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_target_color", "index": index},
                        options=columns,
                        value="Clusters",
                    ),
                    css_class="dd-double-left",
                    title="target (color)",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_target_symbol", "index": index},
                        options=columns,
                    ),
                    css_class="dd-double-right",
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
                    css_class="slider-single",
                    title="jitter",
                ),
            ],
            id={"type": "scatterplot-container", "index": index},
            className="plots",
        )