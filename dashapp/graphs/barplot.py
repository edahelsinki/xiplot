import warnings

import numpy as np
import pandas as pd

import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH

from dashapp.utils.layouts import layout_wrapper, delete_button
from dashapp.graphs import Graph

from collections import Counter


class Barplot(Graph):
    @staticmethod
    def name() -> str:
        return "Barplot"

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "barplot", "index": MATCH}, "figure"),
            Input("selection_cluster_dropdown", "value"),
            Input("comparison_cluster_dropdown", "value"),
            State("data_frame_store", "data"),
            State("clusters_column_store", "data"),
            prevent_initial_call=True,
        )
        def render_barplot(selection, comparison, df, kmeans_col):
            df = df_from_store(df)
            if kmeans_col:
                if len(kmeans_col) == df.shape[0]:
                    df["Clusters"] = kmeans_col
                fig = make_fig_fgs(df, selection, comparison, "reldiff", kmeans_col)
            return fig

        @app.callback(
            Output({"type": "barplot-container", "index": MATCH}, "style"),
            Input({"type": "barplot-delete", "index": MATCH}, "n_clicks"),
            prevent_initial_call=True,
        )
        def delete_barplot(n_clicks):
            return {"display": "none"}

    @staticmethod
    def create_new_layout(index, df, columns):
        return html.Div(
            [
                delete_button("barplot-delete", index),
                dcc.Graph(
                    id={"type": "barplot", "index": index},
                    figure=px.bar(
                        df, columns[6], columns[3]
                    ),  # make_fig_fgs(df, "cl1", "bg", "reldiff", )
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "barplot_x_axis", "index": index},
                        value=columns[0],
                        clearable=False,
                        options=columns,
                    ),
                    title="x axis",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "barplot_y_axis", "index": index},
                        value=columns[1],
                        clearable=False,
                        options=columns,
                    ),
                    title="y axis",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "barplot_cluster_amount", "index": index},
                    ),
                    title="Cluster amount",
                ),
            ],
            id={"type": "barplot-container", "index": index},
            style={"width": "32%", "display": "inline-block", "float": "left"},
        )


def make_fig_fgs(df, cluster, comparison, order, clusters):
    fgs_a = Counter()
    fgs_b = Counter()

    for c, fgs in zip(clusters, df["fgs"]):
        if c == cluster or cluster == "bg":
            fgs_a.update(fgs)

        if c == comparison or comparison == "bg":
            fgs_b.update(fgs)

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
            "fg": [fg for fg, _ in fgs_overall.most_common(10)]
            + [fg for fg, _ in fgs_overall.most_common(10)],
            "frequency": [fgs_a[fg] for fg, _ in fgs_overall.most_common(10)]
            + [fgs_b[fg] for fg, _ in fgs_overall.most_common(10)],
        }
    )

    fig_fgs = px.bar(
        fgs,
        x="fg",
        y="frequency",
        color="Clusters",
        barmode="group",
        hover_data={
            "Clusters": False,
            "fg": False,
            "frequency": ":.2%",
        },
        color_discrete_map={
            "bg": px.colors.qualitative.Plotly[0],
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
