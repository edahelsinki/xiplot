import numpy as np
import pandas as pd
import uuid

import plotly.express as px
import numpy as np
import dash
import jsonschema
import dash_mantine_components as dmc

from collections import defaultdict
from itertools import product

from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate
from xiplot.utils.components import DeleteButton, PdfButton

from xiplot.utils.layouts import layout_wrapper, cluster_dropdown
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.embedding import add_pca_columns_to_df
from xiplot.plots import APlot

from collections.abc import Iterable


class Barplot(APlot):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        PdfButton.register_callback(app, {"type": "barbplot"})

        @app.callback(
            Output({"type": "barplot", "index": MATCH}, "figure"),
            Output({"type": "barplot-notify-container", "index": MATCH}, "children"),
            Input({"type": "barplot_x_axis", "index": MATCH}, "value"),
            Input({"type": "barplot_y_axis", "index": MATCH}, "value"),
            Input({"type": "bp_cluster_comparison_dropdown", "index": MATCH}, "value"),
            Input({"type": "order_dropdown", "index": MATCH}, "value"),
            Input("clusters_column_store", "data"),
            Input("data_frame_store", "data"),
            Input("pca_column_store", "data"),
            prevent_initial_call=False,
        )
        def tmp(x_axis, y_axis, selected_clusters, order, kmeans_col, df, pca_cols):
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except:
                pass

            try:
                return (
                    Barplot.render(
                        x_axis,
                        y_axis,
                        selected_clusters,
                        order,
                        kmeans_col,
                        df_from_store(df),
                        pca_cols,
                    ),
                    dash.no_update,
                )
            except Exception as err:
                return dash.no_update, dmc.Notification(
                    id=str(uuid.uuid4()),
                    color="yellow",
                    title="Warning",
                    message=f"Barplot error: {err}",
                    action="show",
                    autoClose=10000,
                )

        @app.callback(
            output=dict(
                meta=Output("metadata_store", "data"),
            ),
            inputs=[
                State("metadata_store", "data"),
                Input({"type": "barplot_x_axis", "index": ALL}, "value"),
                Input({"type": "barplot_y_axis", "index": ALL}, "value"),
                Input(
                    {"type": "bp_cluster_comparison_dropdown", "index": ALL}, "value"
                ),
                Input({"type": "order_dropdown", "index": ALL}, "value"),
            ],
            prevent_initial_call=False,
        )
        def update_settings(meta, x_axes, y_axes, selected_clusters, order_dropdowns):
            if meta is None:
                return dash.no_update

            for x_axis, y_axis, classes_dropdown, order_dropdown in zip(
                *ctx.args_grouping[1 : 4 + 1]
            ):
                if (
                    not x_axis["triggered"]
                    and not y_axis["triggered"]
                    and not classes_dropdown["triggered"]
                    and not order_dropdown["triggered"]
                ):
                    continue

                index = x_axis["id"]["index"]
                x_axis = x_axis["value"]
                y_axis = y_axis["value"]
                classes_dropdown = classes_dropdown["value"] or []
                order_dropdown = order_dropdown["value"]

                meta["plots"][index] = dict(
                    type=Barplot.name(),
                    axes=dict(x=x_axis, y=y_axis),
                    groupby="Clusters",
                    classes=classes_dropdown,
                    order=order_dropdown,
                )

            return dict(meta=meta)

        @app.callback(
            output=dict(
                barplot_y=Output({"type": "barplot_y_axis", "index": ALL}, "options"),
            ),
            inputs=[
                Input("pca_column_store", "data"),
                State("data_frame_store", "data"),
                State({"type": "barplot_y_axis", "index": ALL}, "options"),
                Input({"type": "barplot", "index": ALL}, "figure"),
            ],
        )
        def update_columns(pca_cols, df, y_all_options, fig):
            df = df_from_store(df)

            if y_all_options:
                y_options = y_all_options[0]
            else:
                return dash.no_update

            if (
                pca_cols
                and len(pca_cols) == df.shape[0]
                and "Xiplot_PCA_1" not in y_options
                and "Xiplot_PCA_2" not in y_options
            ):
                y_options.extend(["Xiplot_PCA_1", "Xiplot_PCA_2"])

            return dict(
                barplot_y=[y_options] * len(y_all_options),
            )

        return [tmp, update_settings]

    @staticmethod
    def render(x_axis, y_axis, selected_clusters, order, kmeans_col, df, pca_cols=[]):
        if len(kmeans_col) == df.shape[0]:
            df["Clusters"] = kmeans_col
        if not "frequency" in df.columns:
            df["frequency"] = [1 for _ in range(len(df))]

        df = add_pca_columns_to_df(df, pca_cols)

        if x_axis == y_axis:
            raise Exception("The x and y axis must be different")

        if not selected_clusters:
            selected_clusters = sorted(set(kmeans_col))
        else:
            selected_clusters = set(selected_clusters)

        Xs = []
        Ys = []
        Cs = []

        if type(df[x_axis][0]) in [np.ndarray, list]:
            if y_axis == "frequency":
                df["frequency"] = [
                    f / max(len(xs), 1) for f, xs in zip(df["frequency"], df[x_axis])
                ]

            for xs, y, c in zip(df[x_axis], df[y_axis], df["Clusters"]):
                for x in xs:
                    if c in selected_clusters:
                        Xs.append(x)
                        Ys.append(y)
                        Cs.append(c)

                    if c != "all" and "all" in selected_clusters:
                        Xs.append(x)
                        Ys.append(y)
                        Cs.append("all")
        else:
            for x, y, c in zip(df[x_axis], df[y_axis], df["Clusters"]):
                if c in selected_clusters:
                    Xs.append(x)
                    Ys.append(y)
                    Cs.append(c)

                if c != "all" and "all" in selected_clusters:
                    Xs.append(x)
                    Ys.append(y)
                    Cs.append("all")

        flat_df = pd.DataFrame(
            {
                x_axis: Xs,
                y_axis: Ys,
                **{
                    "Clusters": Cs
                    for _ in ((),)
                    if x_axis != "Clusters" and y_axis != "Clusters"
                },
            }
        )

        grouping = flat_df.groupby([x_axis, "Clusters"])[y_axis]

        if y_axis == "frequency" and type(df[x_axis][0]) not in [np.ndarray, list]:
            dff = grouping.sum().to_frame().reset_index()
        else:
            dff = grouping.mean().to_frame().reset_index()
            dff["Error"] = grouping.sem().values

        if order == "total" or len(selected_clusters) <= 1:
            order_lookup = defaultdict(lambda: 0.0)

            for x, y in zip(dff[x_axis].values, dff[y_axis].values):
                order_lookup[x] += abs(y)
        elif order == "reldiff":
            value_lookup = defaultdict(list)

            if "Error" in dff.columns:
                for x, y, e in zip(
                    dff[x_axis].values, dff[y_axis].values, dff["Error"].values
                ):
                    value_lookup[x].append((y, e))
            else:
                for x, y in zip(dff[x_axis].values, dff[y_axis].values):
                    value_lookup[x].append((y, 1))

            order_lookup = dict()

            for x, vs in value_lookup.items():
                if len(vs) <= 1:
                    order_lookup[x] = 0.0
                else:
                    maxdiff = 0.0

                    for (v1, e1), (v2, e2) in product(vs, vs):
                        if e1 == 0.0 and e2 == 0.0:
                            e1 = 0.001

                        diff = abs(v1 - v2) / np.sqrt(e1 * e1 + e2 * e2)

                        maxdiff = max(maxdiff, diff)

                    order_lookup[x] = maxdiff

        top_bars = sorted(
            order_lookup.keys(), key=lambda x: order_lookup[x], reverse=True
        )[:10]

        dff.drop(
            index=[i for i, x in zip(dff.index, dff[x_axis]) if x not in top_bars],
            inplace=True,
        )

        fig = px.bar(
            dff,
            x_axis,
            y_axis,
            error_y="Error" if "Error" in dff.columns else None,
            color="Clusters",
            barmode="group",
            hover_data={
                "Clusters": False,
                x_axis: False,
            },
            color_discrete_map=cluster_colours(),
        )

        fig.update_layout(
            hovermode="x unified",
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis=dict(fixedrange=True, categoryorder="array", categoryarray=top_bars),
            yaxis=dict(fixedrange=True),
        )

        return fig

    @staticmethod
    def create_layout(index, df, columns, config=dict()):
        x_columns = [
            c
            for c in columns
            if isinstance(df[c][0], Iterable)
            or df[c].dtype in (int, np.int32, np.int64)
        ]
        y_columns = ["frequency"] + get_numeric_columns(df, columns)

        jsonschema.validate(
            instance=config,
            schema=dict(
                type="object",
                properties=dict(
                    axes=dict(
                        type="object",
                        properties=dict(
                            x=dict(enum=x_columns),
                            y=dict(enum=y_columns),
                        ),
                    ),
                    groupby=dict(enum=["Clusters"]),
                    classes=dict(
                        type="array",
                        items=dict(
                            enum=list(cluster_colours().keys()),
                        ),
                        uniqueItems=True,
                    ),
                ),
                dependentRequired=dict(
                    classes=["groupby"],
                    groupby=["classes"],
                ),
                order=dict(enum=["reldiff", "total"]),
            ),
        )

        try:
            x_axis = config["axes"]["x"]
        except Exception:
            x_axis = None

        if x_axis is None and len(x_columns) > 0:
            x_axis = x_columns[0]

        if x_axis is None:
            raise Exception(
                "The dataframe contains no integer or iterable-categorical columns"
            )

        try:
            y_axis = config["axes"]["y"]
        except Exception:
            y_axis = "frequency"

        if x_axis == y_axis:
            raise Exception("The x and y axis must be different")

        groupby = config.get("groupby", "Clusters")
        classes = config.get("classes", [])
        order = config.get("order", "reldiff")

        return [
            dcc.Graph(
                id={"type": "barplot", "index": index},
                figure=Barplot.render(
                    x_axis,
                    y_axis,
                    classes,
                    order,
                    ["all" for _ in range(len(df))],
                    df,
                ),
            ),
            layout_wrapper(
                component=dcc.Dropdown(
                    id={"type": "barplot_x_axis", "index": index},
                    value=x_axis,
                    clearable=False,
                    options=x_columns,
                ),
                css_class="dd-double-left",
                title="x axis",
            ),
            layout_wrapper(
                component=dcc.Dropdown(
                    id={"type": "barplot_y_axis", "index": index},
                    value=y_axis,
                    clearable=False,
                    options=y_columns,
                ),
                css_class="dd-double-right",
                title="y axis",
            ),
            cluster_dropdown(
                "bp_cluster_comparison_dropdown",
                index,
                multi=True,
                value=classes,
                clearable=True,
                title="Cluster Comparison",
                css_class="dd-single cluster-comparison",
            ),
            layout_wrapper(
                component=dcc.Dropdown(
                    id={"type": "order_dropdown", "index": index},
                    value=order,
                    clearable=False,
                    options=["reldiff", "total"],
                ),
                css_class="dd-single",
                title="Comparison Order",
            ),
            html.Div(
                id={"type": "barplot-notify-container", "index": index},
                style={"display": "none"},
            ),
        ]
