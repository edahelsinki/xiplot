import numpy as np
import pandas as pd
import uuid

import plotly.express as px
import dash
import jsonschema
import dash_mantine_components as dmc

from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import layout_wrapper, delete_button, cluster_dropdown
from dashapp.utils.dataframe import get_numeric_columns
from dashapp.utils.cluster import cluster_colours
from dashapp.plots import Plot

from collections import Counter
from collections.abc import Iterable


class Barplot(Plot):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "barplot", "index": MATCH}, "figure"),
            Output({"type": "barplot-notify-container", "index": MATCH}, "children"),
            Input({"type": "barplot_x_axis", "index": MATCH}, "value"),
            Input({"type": "barplot_y_axis", "index": MATCH}, "value"),
            Input({"type": "bp_cluster_comparison_dropdown", "index": MATCH}, "value"),
            Input({"type": "order_dropdown", "index": MATCH}, "value"),
            Input("clusters_column_store", "data"),
            Input("data_frame_store", "data"),
            prevent_initial_call=False,
        )
        def tmp(x_axis, y_axis, selected_clusters, order, kmeans_col, df):
            if ctx.triggered_id == "data_frame_store":
                raise PreventUpdate()
            try:
                return (
                    Barplot.render(
                        x_axis,
                        y_axis,
                        selected_clusters,
                        order,
                        kmeans_col,
                        df_from_store(df),
                    ),
                    dash.no_update,
                )
            except Exception as err:
                return dash.no_update, dmc.Notification(
                    id=str(uuid.uuid4()),
                    color="yellow",
                    title="Warning",
                    message="The barplot's x and y axis must be different.",
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

    @staticmethod
    def render(x_axis, y_axis, selected_clusters, order, kmeans_col, df):
        if len(kmeans_col) == df.shape[0]:
            df["Clusters"] = kmeans_col
        if y_axis == "frequency":
            fig = make_fig_fgs(df, x_axis, y_axis, selected_clusters, order, kmeans_col)

        elif x_axis == y_axis:
            raise Exception("The x and y axis must be different")

        else:
            if type(df[x_axis][0]) in [np.ndarray, list]:
                grouping = df.groupby(df[x_axis].map(tuple))[y_axis].sum()
            else:
                grouping = df.groupby([x_axis])[y_axis].max()

            dff = (
                grouping.to_frame()
                .sort_values([y_axis], ascending=False)
                .head(10)
                .reset_index()
            )
            dff.columns = [x_axis, y_axis]

            fig = px.bar(
                dff,
                x_axis,
                y_axis,
                color_discrete_map=cluster_colours(),
            )
            fig.update_xaxes(tickangle=45)
            fig.update_layout(xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True))
        return fig

    @staticmethod
    def create_new_layout(index, df, columns, config=dict()):
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

        return html.Div(
            [
                delete_button("plot-delete", index),
                dcc.Graph(
                    id={"type": "barplot", "index": index},
                    figure=make_fig_fgs(
                        df, x_axis, "frequency", classes, order, ["all"] * len(df)
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
                    css_class="dd-single",
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
            ],
            id={"type": "barplot-container", "index": index},
            className="plots",
        )


def make_fig_fgs(df, x_axis, y_axis, selected_clusters, order, clusters):
    if type(selected_clusters) == str:
        selected_clusters = [selected_clusters]
    if not selected_clusters:
        selected_clusters = sorted(set(clusters))
    fgs_dict = {"all": Counter()}
    for s in selected_clusters:
        if s != "all":
            fgs_dict[s] = Counter()
    if type(df[x_axis][0]) in (int, np.int32, np.int64, str):
        for c, row in zip(clusters, df[x_axis]):
            if c != "all" and c in selected_clusters:
                fgs_dict[c].update([row])
            fgs_dict["all"].update([row])
    else:
        for c, row in zip(clusters, df[x_axis]):
            if c != "all" and c in selected_clusters:
                fgs_dict[c].update(row)
            fgs_dict["all"].update(row)

    fgs_total = Counter()
    for s in selected_clusters:
        fgs_total += fgs_dict[s]

    fgs_max = {}
    for s in selected_clusters:
        fgs_max[s] = 1 if len(fgs_dict[s]) == 0 else fgs_dict[s].most_common(1)[0][1]

    for s in selected_clusters:
        for fg in fgs_dict[s]:
            fgs_dict[s][fg] = fgs_dict[s][fg] / fgs_max[s]

    if order == "reldiff":
        fgs_overall = Counter()
        for s in selected_clusters:
            fgs_overall += fgs_dict[s]

        for fg in fgs_overall.keys():
            arr = []
            for s in selected_clusters:
                arr.append(fgs_dict[s][fg])
            fgs_overall[fg] = (
                abs(max(arr) - min(arr)) / np.sqrt(fgs_total[fg]) * np.sqrt(min(arr))
            )
    elif order == "total":
        fgs_overall = Counter()
        for s in selected_clusters:
            fgs_overall += fgs_dict[s]

    clusters_col = []
    x = []
    frequencies = []
    for s in selected_clusters:
        clusters_col += [s for _ in fgs_overall.most_common(10)]
        x += [fg for fg, _ in fgs_overall.most_common(10)]
        frequencies += [fgs_dict[s][fg] for fg, _ in fgs_overall.most_common(10)]

    dff = pd.DataFrame({"Clusters": clusters_col, x_axis: x, "frequency": frequencies})
    fig_fgs = px.bar(
        dff,
        x=x_axis,
        y=y_axis,
        color="Clusters",
        barmode="group",
        hover_data={
            "Clusters": False,
            x_axis: False,
            "frequency": ":.2%",
        },
        color_discrete_map=cluster_colours(),
    )

    fig_fgs.update_layout(
        hovermode="x unified",
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(
            fixedrange=True,
            # TODO: Enabling this option freezes the browser,
            # ticklabelposition="inside",
        ),
        yaxis=dict(
            tickformat=".2%",
            fixedrange=True,
        ),
    )

    return fig_fgs
