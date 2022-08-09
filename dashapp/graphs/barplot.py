import numpy as np
import pandas as pd

import plotly.express as px

from dash import html, dcc, Output, Input, MATCH, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import layout_wrapper, delete_button, cluster_dropdown
from dashapp.utils.dataframe import get_numeric_columns
from dashapp.utils.cluster import cluster_colours
from dashapp.graphs import Graph

from collections import Counter
from collections.abc import Iterable


class Barplot(Graph):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "barplot", "index": MATCH}, "figure"),
            Input({"type": "barplot_x_axis", "index": MATCH}, "value"),
            Input({"type": "barplot_y_axis", "index": MATCH}, "value"),
            Input({"type": "bp_cluster_comparison_dropdown", "index": MATCH}, "value"),
            Input({"type": "order_dropdown", "index": MATCH}, "value"),
            Input("clusters_column_store", "data"),
            Input("data_frame_store", "data"),
        )
        def tmp(x_axis, y_axis, selected_clusters, order, kmeans_col, df):
            if ctx.triggered_id == "data_frame_store":
                raise PreventUpdate()

            fig = Barplot.render(
                x_axis,
                y_axis,
                selected_clusters,
                order,
                kmeans_col,
                df_from_store(df),
            )
            if not fig:
                raise PreventUpdate()
            return fig

    @staticmethod
    def render(x_axis, y_axis, selected_clusters, order, kmeans_col, df):
        if len(kmeans_col) == df.shape[0]:
            df["Clusters"] = kmeans_col
        if y_axis == "frequency":
            fig = make_fig_fgs(df, x_axis, y_axis, selected_clusters, order, kmeans_col)

        elif x_axis == y_axis:
            raise PreventUpdate()

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
    def create_new_layout(index, df, columns):
        x = [
            c
            for c in columns
            if isinstance(df[c][0], Iterable)
            or type(df[c][0]) in (int, np.int32, np.int64)
        ]
        y = ["frequency"] + get_numeric_columns(df, columns)
        return html.Div(
            [
                delete_button("plot-delete", index),
                dcc.Graph(
                    id={"type": "barplot", "index": index},
                    figure=make_fig_fgs(
                        df, x[0], "frequency", "all", "reldiff", ["all"] * len(df)
                    ),
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "barplot_x_axis", "index": index},
                        value=x[0],
                        clearable=False,
                        options=x,
                    ),
                    css_class="dd-double-left",
                    title="x axis",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "barplot_y_axis", "index": index},
                        value="frequency",
                        clearable=False,
                        options=y,
                    ),
                    css_class="dd-double-right",
                    title="y axis",
                ),
                cluster_dropdown(
                    "bp_cluster_comparison_dropdown",
                    index,
                    multi=True,
                    value="all",
                    clearable=True,
                    title="Cluster Comparison",
                    css_class="dd-single",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "order_dropdown", "index": index},
                        value="reldiff",
                        clearable=False,
                        options=["reldiff", "total"],
                    ),
                    css_class="dd-single",
                    title="Comparison Order",
                ),
            ],
            id={"type": "barplot-container", "index": index},
            className="graphs",
        )


def make_fig_fgs(df, x_axis, y_axis, selected_clusters, order, clusters):
    if not selected_clusters:
        return None
    if type(selected_clusters) == str:
        selected_clusters = [selected_clusters]
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
