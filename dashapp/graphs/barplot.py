import numpy as np
import pandas as pd

import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH

from dashapp.utils.layouts import layout_wrapper, delete_button, cluster_dropdown
from dashapp.utils.dataframe import get_numeric_columns
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
            Input({"type": "bp_selection_cluster_dropdown", "index": MATCH}, "value"),
            Input({"type": "bp_comparison_cluster_dropdown", "index": MATCH}, "value"),
            Input("clusters_column_store", "data"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def tmp(x_axis, y_axis, selection, comparison, kmeans_col, df):
            return Barplot.render_barplot(
                x_axis, y_axis, selection, comparison, kmeans_col, df_from_store(df)
            )

    @staticmethod
    def render_barplot(x_axis, y_axis, selection, comparison, kmeans_col, df):
        if len(kmeans_col) == df.shape[0]:
            df["Clusters"] = kmeans_col
        if y_axis == "frequency":
            fig = make_fig_fgs(
                df, x_axis, y_axis, selection, comparison, "reldiff", kmeans_col
            )
        else:
            fig = px.bar(
                df,
                x_axis,
                y_axis,
                color="Clusters",
                color_discrete_map={
                    "all": px.colors.qualitative.Plotly[0],
                    **{
                        f"c{i+1}": c
                        for i, c in enumerate(px.colors.qualitative.Plotly[1:])
                    },
                    "bg\u00A0": px.colors.qualitative.Plotly[0],
                    **{
                        f"c{i+1}\u00A0": c
                        for i, c in enumerate(px.colors.qualitative.Plotly[1:])
                    },
                },
            )
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
                    figure=px.bar(
                        df, columns[6], columns[3]
                    ),  # make_fig_fgs(df, "cl1", "bg", "reldiff", )
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
                        value=y[0],
                        clearable=False,
                        options=y,
                    ),
                    css_class="dd-double-right",
                    title="y axis",
                ),
                cluster_dropdown(
                    "bp_selection_cluster_dropdown", index, selection=True
                ),
                cluster_dropdown(
                    "bp_comparison_cluster_dropdown", index, selection=False
                ),
            ],
            id={"type": "barplot-container", "index": index},
            className="graphs",
        )


def make_fig_fgs(df, x_axis, y_axis, cluster, comparison, order, clusters):
    fgs_a = Counter()
    fgs_b = Counter()

    if type(df[x_axis][0]) in (int, np.int32, np.int64, str):
        for c, row in zip(clusters, df[x_axis]):
            if c == cluster or cluster == "all":
                fgs_a.update([row])
            if c == comparison or comparison == "all":
                fgs_b.update([row])
    else:
        for c, row in zip(clusters, df[x_axis]):
            if c == cluster or cluster == "all":
                fgs_a.update(row)

            if c == comparison or comparison == "all":
                fgs_b.update(row)

    comparison += "\u00A0"

    fgs_total = fgs_a + fgs_b

    fgs_a_max = 1 if len(fgs_a) == 0 else fgs_a.most_common(1)[0][1]
    fgs_b_max = 1 if len(fgs_b) == 0 else fgs_b.most_common(1)[0][1]

    for fg in fgs_a.keys():
        fgs_a[fg] = fgs_a[fg] / fgs_a_max

    for fg in fgs_b.keys():
        fgs_b[fg] = fgs_b[fg] / fgs_b_max

    if order == "reldiff":
        fgs_overall = fgs_a + fgs_b

        for fg in fgs_overall.keys():
            fgs_overall[fg] = (
                abs(fgs_a[fg] - fgs_b[fg])
                / np.sqrt(fgs_total[fg])
                * np.sqrt(min(fgs_a[fg], fgs_b[fg]))
            )
    elif order == "selection":
        fgs_overall = fgs_a
    elif order == "comparison":
        fgs_overall = fgs_b
    else:
        fgs_overall = fgs_a + fgs_b

    fgs = pd.DataFrame(
        {
            "Clusters": [cluster for _ in fgs_overall.most_common(10)]
            + [comparison for _ in fgs_overall.most_common(10)],
            x_axis: [fg for fg, _ in fgs_overall.most_common(10)]
            + [fg for fg, _ in fgs_overall.most_common(10)],
            y_axis: [fgs_a[fg] for fg, _ in fgs_overall.most_common(10)]
            + [fgs_b[fg] for fg, _ in fgs_overall.most_common(10)],
        }
    )

    fig_fgs = px.bar(
        fgs,
        x=x_axis,
        y=y_axis,
        color="Clusters",
        barmode="group",
        hover_data={
            "Clusters": False,
            x_axis: False,
            "frequency": ":.2%",
        },
        color_discrete_map={
            "all": px.colors.qualitative.Plotly[0],
            **{f"c{i+1}": c for i, c in enumerate(px.colors.qualitative.Plotly[1:])},
            "bg\u00A0": px.colors.qualitative.Plotly[0],
            **{
                f"c{i+1}\u00A0": c
                for i, c in enumerate(px.colors.qualitative.Plotly[1:])
            },
        },
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
