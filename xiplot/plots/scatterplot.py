import json
import uuid

import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import ALL, MATCH, Input, Output, State, ctx, dcc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput

from xiplot.plots import APlot
from xiplot.tabs.cluster import CLUSTER_COLUMN_NAME, get_clusters
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.components import ColumnDropdown, PdfButton, PlotData
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.layouts import layout_wrapper
from xiplot.utils.scatterplot import get_row


class Scatterplot(APlot):
    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        PdfButton.register_callback(app, {"type": "scatterplot"})

        @app.callback(
            Output({"type": "scatterplot", "index": MATCH}, "figure"),
            Input(cls.get_id(MATCH, "x_axis_dropdown"), "value"),
            Input(cls.get_id(MATCH, "y_axis_dropdown"), "value"),
            Input(cls.get_id(MATCH, "color_dropdown"), "value"),
            Input(cls.get_id(MATCH, "symbol_dropdown"), "value"),
            Input({"type": "jitter-slider", "index": MATCH}, "value"),
            Input("selected_rows_store", "data"),
            Input("data_frame_store", "data"),
            Input("auxiliary_store", "data"),
            Input("plotly-template", "data"),
            prevent_initial_call=False,
        )
        def tmp(
            x_axis,
            y_axis,
            color,
            symbol,
            jitter,
            selected_rows,
            df,
            aux,
            template=None,
        ):
            # Try branch for testing
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except Exception:
                pass

            fig = Scatterplot.render(
                df_from_store(df),
                df_from_store(aux),
                x_axis,
                y_axis,
                color,
                symbol,
                jitter,
                selected_rows,
                template,
            )

            if fig is None:
                return dash.no_update

            return fig

        @app.callback(
            Output({"type": "jitter-slider", "index": MATCH}, "max"),
            Input({"type": "x_axis_dropdown", "index": MATCH}, "value"),
            State("data_frame_store", "data"),
        )
        def update_jitter_max(x_axis, df):
            df = df_from_store(df)
            if x_axis in df.columns.to_list():
                return (df[x_axis].max() - df[x_axis].min()) * 0.05
            return dash.no_update

        @app.callback(
            output=dict(
                selected_rows_store=Output("selected_rows_store", "data"),
                click_store=Output("lastly_clicked_point_store", "data"),
                scatter=Output(
                    {"type": "scatterplot", "index": ALL}, "clickData"
                ),
            ),
            inputs=[
                Input({"type": "scatterplot", "index": ALL}, "clickData"),
                State("selected_rows_store", "data"),
            ],
        )
        def handle_click_events(click, selected_rows):
            # Try branch for testing
            try:
                if ctx.triggered_id is None:
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except Exception:
                pass

            if not selected_rows:
                selected_rows = []

            row = get_row(click)
            if row is None:
                raise PreventUpdate()

            if not selected_rows[row]:
                selected_rows[row] = True
            else:
                selected_rows[row] = False

            scatter_amount = len(click)

            return dict(
                selected_rows_store=selected_rows,
                click_store=row,
                scatter=[None] * scatter_amount,
            )

        @app.callback(
            output=dict(
                hover_store=Output("lastly_hovered_point_store", "data"),
                scatter=Output(
                    {"type": "scatterplot", "index": ALL}, "hoverData"
                ),
            ),
            inputs=[
                Input({"type": "scatterplot", "index": ALL}, "hoverData"),
            ],
        )
        def handle_hover_events(hover):
            row = get_row(hover)
            if row is None:
                raise PreventUpdate()

            scatter_amount = len(hover)
            return dict(
                hover_store=row,
                scatter=[None] * scatter_amount,
            )

        @app.callback(
            output=dict(
                aux=ServersideOutput("auxiliary_store", "data"),
                reset=Output("clusters_column_store_reset", "children"),
            ),
            inputs=[
                Input({"type": "scatterplot", "index": ALL}, "selectedData"),
                State("auxiliary_store", "data"),
                State("selection_cluster_dropdown", "value"),
                State("cluster_selection_mode", "value"),
            ],
        )
        def handle_cluster_drawing(
            selected_data, aux, cluster_id, selection_mode
        ):
            if not selected_data:
                return dash.no_update

            updated = False

            aux = df_from_store(aux)
            clusters = get_clusters(aux)
            if not selection_mode:
                clusters = clusters.set_categories(["c1", "c2"])
                clusters[:] = "c2"
            else:
                if cluster_id not in clusters.categories:
                    clusters = clusters.add_categories([cluster_id])

            try:
                for trigger in ctx.triggered:
                    if (
                        not trigger
                        or not trigger["value"]
                        or not trigger["value"]["points"]
                    ):
                        continue

                    updated = updated or len(trigger["value"]["points"]) > 0

                    try:
                        if selection_mode:
                            for p in trigger["value"]["points"]:
                                clusters[
                                    p["customdata"][0]["index"]
                                ] = cluster_id
                        else:
                            for p in trigger["value"]["points"]:
                                clusters[p["customdata"][0]["index"]] = "c1"
                    except Exception:
                        return dash.no_update
            # Try branch for testing
            except Exception:
                trigger = {
                    "value": {"points": [{"customdata": [{"index": 1}]}]}
                }

                updated = updated or len(trigger["value"]["points"]) > 0

                try:
                    if selection_mode:
                        for p in trigger["value"]["points"]:
                            clusters[p["customdata"][0]["index"]] = cluster_id
                    else:
                        for p in trigger["value"]["points"]:
                            clusters[p["customdata"][0]["index"]] = "c1"
                except Exception:
                    return dash.no_update

            if not updated:
                return dash.no_update

            aux[CLUSTER_COLUMN_NAME] = clusters
            return dict(aux=df_to_store(aux), reset=str(uuid.uuid4()))

        PlotData.register_callback(
            cls.name(),
            app,
            (
                Input(cls.get_id(MATCH, "x_axis_dropdown"), "value"),
                Input(cls.get_id(MATCH, "y_axis_dropdown"), "value"),
                Input(cls.get_id(MATCH, "color_dropdown"), "value"),
                Input(cls.get_id(MATCH, "symbol_dropdown"), "value"),
                Input({"type": "jitter-slider", "index": MATCH}, "value"),
            ),
            lambda i: dict(
                axes=dict(x=i[0], y=i[1]),
                colour=i[2],
                symbol=i[3],
                jitter=i[4],
            ),
        )

        ColumnDropdown.register_callback(
            app,
            cls.get_id(ALL, "x_axis_dropdown"),
            df_from_store,
            numeric=True,
        )
        ColumnDropdown.register_callback(
            app,
            cls.get_id(ALL, "y_axis_dropdown"),
            df_from_store,
            numeric=True,
        )
        ColumnDropdown.register_callback(
            app,
            cls.get_id(ALL, "color_dropdown"),
            df_from_store,
        )
        ColumnDropdown.register_callback(
            app,
            cls.get_id(ALL, "symbol_dropdown"),
            df_from_store,
            category=True,
        )

        return [
            tmp,
            handle_click_events,
            handle_hover_events,
            handle_cluster_drawing,
        ]

    @staticmethod
    def render(
        df,
        aux,
        x_axis,
        y_axis,
        color=None,
        symbol=None,
        jitter=None,
        selected_rows=None,
        template=None,
    ):
        df = pd.concat((df, aux), axis=1)
        if jitter:
            jitter = float(jitter)
        if type(jitter) == float:
            if jitter > 0:
                Z = df[[x_axis, y_axis]].to_numpy("float64")
                Z = np.random.normal(Z, jitter)
                jitter_df = pd.DataFrame(Z, columns=[x_axis, y_axis])

                # Distinguish axes' names if identical
                if x_axis == y_axis:
                    jitter_df.columns = [x_axis + "(1)", x_axis + "(2)"]

                df[["jitter-x", "jitter-y"]] = jitter_df

                # Set jitter results to the axes but keep the title of the axes
                x_title, y_title = x_axis, y_axis
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
            template=template,
        )
        fig.update_layout(
            showlegend=False, uirevision=json.dumps([x_axis, y_axis])
        )
        fig.update(layout_coloraxis_showscale=False)
        fig.update_traces(marker={"line": {"width": 0}})

        if jitter:
            fig.update_xaxes(title=x_title)
            fig.update_yaxes(title=y_title)

        return fig

    @classmethod
    def create_layout(cls, index, df, columns, config=dict()):
        num_columns = get_numeric_columns(df, columns)

        try:
            x_axis = config["axes"]["x"]
        except Exception:
            x_axis = None

        try:
            y_axis = config["axes"]["y"]
        except Exception:
            y_axis = None

        scatter_colour = config.get("colour", CLUSTER_COLUMN_NAME)
        scatter_symbol = config.get("symbol", None)
        jitter_slider = config.get("jitter", 0.0)

        for c in num_columns:
            if x_axis is None and ("x-" in c or " 1" in c):
                x_axis = c

            if y_axis is None and ("y-" in c or " 2" in c):
                y_axis = c

        if x_axis is None and len(num_columns) > 0:
            x_axis = num_columns[0]

        if y_axis is None and len(num_columns) > 0:
            y_axis = num_columns[min(1, len(num_columns) - 1)]

        if x_axis is None or y_axis is None:
            raise Exception("The dataframe contains no numeric columns")

        df["__Auxiliary__"] = [{"index": i} for i in range(len(df))]

        return [
            dcc.Graph(id={"type": "scatterplot", "index": index}),
            layout_wrapper(
                component=ColumnDropdown(
                    cls.get_id(index, "x_axis_dropdown"),
                    options=num_columns,
                    value=x_axis,
                    clearable=False,
                ),
                css_class="dd-double-left",
                title="x",
            ),
            layout_wrapper(
                component=ColumnDropdown(
                    cls.get_id(index, "y_axis_dropdown"),
                    options=num_columns,
                    value=y_axis,
                    clearable=False,
                ),
                css_class="dd-double-right",
                title="y",
            ),
            layout_wrapper(
                component=ColumnDropdown(
                    cls.get_id(index, "color_dropdown"),
                    options=columns,
                    value=scatter_colour,
                    clearable=False,
                ),
                css_class="dd-double-left",
                title="target (color)",
            ),
            layout_wrapper(
                component=ColumnDropdown(
                    cls.get_id(index, "symbol_dropdown"),
                    options=columns,
                    value=scatter_symbol,
                ),
                css_class="dd-double-right",
                title="target (symbol)",
            ),
            layout_wrapper(
                component=dcc.Slider(
                    id={"type": "jitter-slider", "index": index},
                    min=0,
                    max=1,
                    value=jitter_slider,
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
                css_class="slider-single",
                title="jitter",
            ),
        ]
