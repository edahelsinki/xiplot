import uuid
from collections import defaultdict
from itertools import product

import dash
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import MATCH, Input, Output, ctx, dcc, html
from dash.exceptions import PreventUpdate

from xiplot.plots import APlot
from xiplot.plugin import ID_HOVERED
from xiplot.utils.auxiliary import (
    SELECTED_COLUMN_NAME,
    decode_aux,
    get_clusters,
    merge_df_aux,
)
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.components import (
    ClusterDropdown,
    ColumnDropdown,
    PdfButton,
    PlotData,
)
from xiplot.utils.layouts import layout_wrapper


class Barplot(APlot):
    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        PdfButton.register_callback(app, cls.name(), {"type": "barplot"})

        @app.callback(
            Output({"type": "barplot", "index": MATCH}, "figure"),
            Output(
                {"type": "barplot-notify-container", "index": MATCH},
                "children",
            ),
            Input(cls.get_id(MATCH, "x_axis_dropdown"), "value"),
            Input(cls.get_id(MATCH, "y_axis_dropdown"), "value"),
            Input(ClusterDropdown.get_id(MATCH), "value"),
            Input({"type": "order_dropdown", "index": MATCH}, "value"),
            Input(ID_HOVERED, "data"),
            Input("data_frame_store", "data"),
            Input("auxiliary_store", "data"),
            Input("plotly-template", "data"),
            prevent_initial_call=False,
        )
        def tmp(
            x_axis,
            y_axis,
            selected_clusters,
            order,
            hover,
            df,
            aux,
            template=None,
        ):
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except Exception:
                pass

            try:
                return (
                    Barplot.render(
                        x_axis,
                        y_axis,
                        selected_clusters,
                        order,
                        hover,
                        df_from_store(df),
                        decode_aux(aux),
                        template,
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

        PlotData.register_callback(
            cls.name(),
            app,
            [
                Input(cls.get_id(MATCH, "x_axis_dropdown"), "value"),
                Input(cls.get_id(MATCH, "y_axis_dropdown"), "value"),
                Input(ClusterDropdown.get_id(MATCH), "value"),
                Input({"type": "order_dropdown", "index": MATCH}, "value"),
            ],
            lambda i: dict(
                axes=dict(x=i[0], y=i[1]),
                classes=i[2] or [],
                order=i[3],
            ),
        )

        ColumnDropdown.register_callback(
            app,
            cls.get_id(MATCH, "x_axis_dropdown"),
            df_from_store,
            category=True,
        )
        ColumnDropdown.register_callback(
            app,
            cls.get_id(MATCH, "y_axis_dropdown"),
            df_from_store,
            options=["frequency"],
            numeric=True,
        )

        return [tmp]

    @staticmethod
    def render(
        x_axis,
        y_axis,
        selected_clusters,
        order,
        hover,
        df,
        aux,
        template=None,
    ):
        df = merge_df_aux(df, aux)
        if "frequency" not in df.columns:
            df["frequency"] = [1 for _ in range(len(df))]

        if x_axis == y_axis:
            raise Exception("The x and y axis must be different")

        clusters = get_clusters(aux, df.shape[0])
        if not selected_clusters:
            selected_clusters = clusters.categories
        selected_clusters = set(selected_clusters)

        Xs = []
        Ys = []
        Cs = []

        if type(df[x_axis][0]) in [np.ndarray, list]:
            if y_axis == "frequency":
                df["frequency"] = [
                    f / max(len(xs), 1)
                    for f, xs in zip(df["frequency"], df[x_axis])
                ]

            for xs, y, c in zip(df[x_axis], df[y_axis], clusters):
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
            for x, y, c in zip(df[x_axis], df[y_axis], clusters):
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

        if y_axis == "frequency" and type(df[x_axis][0]) not in [
            np.ndarray,
            list,
        ]:
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
            index=[
                i for i, x in zip(dff.index, dff[x_axis]) if x not in top_bars
            ],
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
            template=template,
        )

        fig.update_layout(
            hovermode="x unified",
            showlegend=False,
            xaxis=dict(
                fixedrange=True, categoryorder="array", categoryarray=top_bars
            ),
            yaxis=dict(fixedrange=True),
        )

        if y_axis != "frequency":
            if hover is not None:
                fig.add_hline(
                    df[y_axis][hover],
                    line=dict(color="rgba(0.5,0.5,0.5,0.5)", dash="dash"),
                    layer="below",
                )

            if SELECTED_COLUMN_NAME in aux:
                color = "#DDD" if template and "dark" in template else "#333"
                for x in df[y_axis][aux[SELECTED_COLUMN_NAME]]:
                    fig.add_hline(
                        x, line=dict(color=color, width=0.5), layer="below"
                    )

        return fig

    @classmethod
    def create_layout(cls, index, df, columns, config=dict()):
        import jsonschema

        x_columns = ColumnDropdown.get_columns(
            df, pd.DataFrame(), category=True
        )
        y_columns = ColumnDropdown.get_columns(
            df, pd.DataFrame(), ["frequency"], numeric=True
        )
        jsonschema.validate(
            instance=config,
            schema=dict(
                type="object",
                properties=dict(
                    axes=dict(
                        type="object",
                        properties=dict(
                            x=dict(type="string"), y=dict(type="string")
                        ),
                    ),
                    classes=dict(
                        type="array",
                        items=dict(enum=list(cluster_colours().keys())),
                        uniqueItems=True,
                    ),
                    order=dict(enum=["reldiff", "total"]),
                ),
            ),
        )

        try:
            x_axis = config["axes"]["x"]
        except Exception:
            x_axis = None

        if x_axis is None and len(x_columns) > 0:
            x_axis = x_columns[0]

        try:
            y_axis = config["axes"]["y"]
        except Exception:
            y_axis = "frequency"

        if x_axis == y_axis:
            raise Exception("The x and y axis must be different")

        classes = config.get("classes", [])
        order = config.get("order", "reldiff")

        return [
            dcc.Graph(id={"type": "barplot", "index": index}),
            layout_wrapper(
                component=ColumnDropdown(
                    cls.get_id(index, "x_axis_dropdown"),
                    value=x_axis,
                    clearable=False,
                    options=x_columns,
                ),
                css_class="dd-double-left",
                title="x axis",
            ),
            layout_wrapper(
                component=ColumnDropdown(
                    cls.get_id(index, "y_axis_dropdown"),
                    value=y_axis,
                    clearable=False,
                    options=y_columns,
                ),
                css_class="dd-double-right",
                title="y axis",
            ),
            layout_wrapper(
                component=ClusterDropdown(
                    index=index, multi=True, value=classes, clearable=True
                ),
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
