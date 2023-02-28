import json
import uuid

import dash
import numpy as np
import pandas as pd
import plotly.express as px
import jsonschema

from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate
from xiplot.utils.components import DeleteButton, PdfButton

from xiplot.utils.layouts import layout_wrapper
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.scatterplot import get_row
from xiplot.utils.embedding import add_pca_columns_to_df
from xiplot.plots import APlot


class Scatterplot(APlot):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        PdfButton.register_callback(app, {"type": "scatterplot"})

        @app.callback(
            Output({"type": "scatterplot", "index": MATCH}, "figure"),
            Input({"type": "scatter_x_axis", "index": MATCH}, "value"),
            Input({"type": "scatter_y_axis", "index": MATCH}, "value"),
            Input({"type": "scatter_target_color", "index": MATCH}, "value"),
            Input({"type": "scatter_target_symbol", "index": MATCH}, "value"),
            Input({"type": "jitter-slider", "index": MATCH}, "value"),
            Input("selected_rows_store", "data"),
            Input("clusters_column_store", "data"),
            Input("data_frame_store", "data"),
            Input("pca_column_store", "data"),
            prevent_initial_call=False,
        )
        def tmp(
            x_axis,
            y_axis,
            color,
            symbol,
            jitter,
            selected_rows,
            kmeans_col,
            df,
            pca_cols,
        ):
            # Try branch for testing
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except:
                pass

            df = df_from_store(df)
            fig = Scatterplot.render(
                df,
                x_axis,
                y_axis,
                color,
                symbol,
                jitter,
                selected_rows,
                kmeans_col,
                pca_cols,
            )

            if fig is None:
                return dash.no_update

            return fig

        @app.callback(
            Output({"type": "jitter-slider", "index": MATCH}, "max"),
            Input({"type": "scatter_x_axis", "index": MATCH}, "value"),
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
                scatter=Output({"type": "scatterplot", "index": ALL}, "clickData"),
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
            except:
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

            scatter_amount = len(hover)
            return dict(
                hover_store=row,
                scatter=[None] * scatter_amount,
            )

        @app.callback(
            output=dict(
                clusters=Output("clusters_column_store", "data"),
                reset=Output("clusters_column_store_reset", "children"),
            ),
            inputs=[
                Input({"type": "scatterplot", "index": ALL}, "selectedData"),
                State("clusters_column_store", "data"),
                State("selection_cluster_dropdown", "value"),
                State("cluster_selection_mode", "value"),
            ],
        )
        def handle_cluster_drawing(
            selected_data, kmeans_col, cluster_id, selection_mode
        ):
            if not selected_data:
                return dash.no_update

            updated = False

            if not selection_mode:
                kmeans_col = ["c2"] * len(kmeans_col)

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
                                kmeans_col[p["customdata"][0]["index"]] = cluster_id
                        else:
                            for p in trigger["value"]["points"]:
                                kmeans_col[p["customdata"][0]["index"]] = "c1"
                    except Exception:
                        return dash.no_update
            # Try branch for testing
            except:
                trigger = {"value": {"points": [{"customdata": [{"index": 1}]}]}}

                updated = updated or len(trigger["value"]["points"]) > 0

                try:
                    if selection_mode:
                        for p in trigger["value"]["points"]:
                            kmeans_col[p["customdata"][0]["index"]] = cluster_id
                    else:
                        for p in trigger["value"]["points"]:
                            kmeans_col[p["customdata"][0]["index"]] = "c1"
                except Exception:
                    return dash.no_update

            if not updated:
                return dash.no_update

            return dict(clusters=kmeans_col, reset=str(uuid.uuid4()))

        @app.callback(
            output=dict(
                meta=Output("metadata_store", "data"),
            ),
            inputs=[
                State("metadata_store", "data"),
                Input({"type": "scatter_x_axis", "index": ALL}, "value"),
                Input({"type": "scatter_y_axis", "index": ALL}, "value"),
                Input({"type": "scatter_target_color", "index": ALL}, "value"),
                Input({"type": "scatter_target_symbol", "index": ALL}, "value"),
                Input({"type": "jitter-slider", "index": ALL}, "value"),
            ],
            prevent_initial_call=False,
        )
        def update_settings(
            meta, x_axes, y_axes, scatter_colours, scatter_symbols, jitter_sliders
        ):
            if meta is None:
                return dash.no_update

            for x_axis, y_axis, scatter_colour, scatter_symbol, jitter_slider in zip(
                *ctx.args_grouping[1 : 5 + 1]
            ):
                if (
                    not x_axis["triggered"]
                    and not y_axis["triggered"]
                    and not scatter_colour["triggered"]
                    and not scatter_symbol["triggered"]
                    and not jitter_slider["triggered"]
                ):
                    continue

                index = x_axis["id"]["index"]
                x_axis = x_axis["value"]
                y_axis = y_axis["value"]
                scatter_colour = scatter_colour["value"]
                scatter_symbol = scatter_symbol["value"]
                jitter_slider = jitter_slider["value"]

                meta["plots"][index] = dict(
                    type=Scatterplot.name(),
                    axes=dict(x=x_axis, y=y_axis),
                    colour=scatter_colour,
                    symbol=scatter_symbol,
                    jitter=jitter_slider,
                )

            return dict(meta=meta)

        @app.callback(
            output=dict(
                scatter_x=Output({"type": "scatter_x_axis", "index": ALL}, "options"),
                scatter_y=Output({"type": "scatter_y_axis", "index": ALL}, "options"),
            ),
            inputs=[
                Input("pca_column_store", "data"),
                State("data_frame_store", "data"),
                State({"type": "scatter_y_axis", "index": ALL}, "options"),
                Input({"type": "scatterplot", "index": ALL}, "figure"),
            ],
        )
        def update_columns(pca_cols, df, all_options, fig):
            df = df_from_store(df)

            if all_options:
                options = all_options[0]
            else:
                return dash.no_update

            if (
                pca_cols
                and len(pca_cols) == df.shape[0]
                and "Xiplot_PCA_1" not in options
                and "Xiplot_PCA_2" not in options
            ):
                options.extend(["Xiplot_PCA_1", "Xiplot_PCA_2"])

            return dict(
                scatter_x=[options] * len(all_options),
                scatter_y=[options] * len(all_options),
            )

        return [
            tmp,
            handle_click_events,
            handle_hover_events,
            handle_cluster_drawing,
            update_settings,
        ]

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
        pca_cols=[],
    ):
        if x_axis in ["Xiplot_PCA_1", "Xiplot_PCA_2"] and not pca_cols:
            return None

        if len(kmeans_col) == df.shape[0]:
            df["Clusters"] = kmeans_col
        else:
            df["Clusters"] = ["all"] * df.shape[0]

        df = add_pca_columns_to_df(df, pca_cols)

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
    def create_new_layout(index, df, columns, config=dict()):
        num_columns = get_numeric_columns(df, columns)

        jsonschema.validate(
            instance=config,
            schema=dict(
                type="object",
                properties=dict(
                    axes=dict(
                        type="object",
                        properties=dict(
                            x=dict(enum=num_columns),
                            y=dict(enum=num_columns),
                        ),
                    ),
                    colour=dict(enum=columns + [None]),
                    symbol=dict(enum=columns + [None]),
                    jitter=dict(type="number", minimum=0.0),
                ),
            ),
        )

        try:
            x_axis = config["axes"]["x"]
        except Exception:
            x_axis = None

        try:
            y_axis = config["axes"]["y"]
        except Exception:
            y_axis = None

        scatter_colour = config.get("colour", "Clusters")
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

        return html.Div(
            children=[
                DeleteButton(index),
                PdfButton(index),
                dcc.Graph(
                    id={"type": "scatterplot", "index": index},
                    figure=px.scatter(
                        df,
                        x_axis,
                        y_axis,
                        custom_data=["__Auxiliary__"],
                        render_mode="webgl",
                    ),
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_x_axis", "index": index},
                        options=num_columns,
                        value=x_axis,
                        clearable=False,
                    ),
                    css_class="dd-double-left",
                    title="x",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_y_axis", "index": index},
                        options=num_columns,
                        value=y_axis,
                        clearable=False,
                    ),
                    css_class="dd-double-right",
                    title="y",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_target_color", "index": index},
                        options=columns,
                        value=scatter_colour,
                        clearable=False,
                    ),
                    css_class="dd-double-left",
                    title="target (color)",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_target_symbol", "index": index},
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
            ],
            id={"type": "scatterplot-container", "index": index},
            className="plots",
        )
