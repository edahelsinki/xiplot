import pandas as pd
import plotly.express as px
import jsonschema
import dash

from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate
from xiplot.utils.components import DeleteButton, PdfButton

from xiplot.utils.layouts import layout_wrapper, cluster_dropdown
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.embedding import add_pca_columns_to_df
from xiplot.plots import APlot


class Histogram(APlot):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        PdfButton.register_callback(app, {"type": "histogram"})

        @app.callback(
            Output({"type": "histogram", "index": MATCH}, "figure"),
            Input({"type": "x_axis_histo", "index": MATCH}, "value"),
            Input({"type": "hg_cluster_comparison_dropdown", "index": MATCH}, "value"),
            Input("clusters_column_store", "data"),
            Input("data_frame_store", "data"),
            Input("pca_column_store", "data"),
            prevent_initial_call=False,
        )
        def tmp(x_axis, selected_clusters, kmeans_col, df, pca_cols):
            # Try branch for testing
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except:
                pass

            return Histogram.render(
                x_axis, selected_clusters, kmeans_col, df_from_store(df), pca_cols
            )

        @app.callback(
            output=dict(
                meta=Output("metadata_store", "data"),
            ),
            inputs=[
                State("metadata_store", "data"),
                Input({"type": "x_axis_histo", "index": ALL}, "value"),
                Input(
                    {"type": "hg_cluster_comparison_dropdown", "index": ALL}, "value"
                ),
            ],
            prevent_initial_call=False,
        )
        def update_settings(meta, x_axes, classes_dropdowns):
            if meta is None:
                return dash.no_update

            for x_axis, classes_dropdown in zip(*ctx.args_grouping[1 : 2 + 1]):
                if not x_axis["triggered"] and not classes_dropdown["triggered"]:
                    continue

                index = x_axis["id"]["index"]
                x_axis = x_axis["value"]
                classes_dropdown = classes_dropdown["value"] or []

                meta["plots"][index] = dict(
                    type=Histogram.name(),
                    axes=dict(x=x_axis),
                    groupby="Clusters",
                    classes=classes_dropdown,
                )

            return dict(meta=meta)

        @app.callback(
            output=dict(
                histogram_x=Output({"type": "x_axis_histo", "index": ALL}, "options"),
            ),
            inputs=[
                Input("pca_column_store", "data"),
                State("data_frame_store", "data"),
                State({"type": "x_axis_histo", "index": ALL}, "options"),
                Input({"type": "histogram", "index": ALL}, "figure"),
            ],
        )
        def update_columns(pca_cols, df, x_all_options, fig):
            df = df_from_store(df)

            if x_all_options:
                x_options = x_all_options[0]
            else:
                return dash.no_update

            if (
                pca_cols
                and len(pca_cols) == df.shape[0]
                and "Xiplot_PCA_1" not in x_options
                and "Xiplot_PCA_2" not in x_options
            ):
                x_options.extend(["Xiplot_PCA_1", "Xiplot_PCA_2"])

            return dict(
                histogram_x=[x_options] * len(x_all_options),
            )

        return [tmp, update_settings]

    @staticmethod
    def render(x_axis, selected_clusters, kmeans_col, df, pca_cols=[]):
        if len(kmeans_col) == df.shape[0]:
            df["Clusters"] = kmeans_col

        df = add_pca_columns_to_df(df, pca_cols)

        fig = make_fig_property(df, x_axis, selected_clusters, kmeans_col)

        return fig

    @staticmethod
    def create_layout(index, df, columns, config=dict()):
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
            ),
        )

        try:
            x_axis = config["axes"]["x"]
        except Exception:
            x_axis = None

        if x_axis is None and len(num_columns) > 0:
            x_axis = num_columns[0]

        if x_axis is None:
            raise Exception("The dataframe contains no numeric columns")

        groupby = config.get("groupby", "Clusters")
        classes = config.get("classes", [])

        return [
            dcc.Graph(
                id={"type": "histogram", "index": index},
                figure=make_fig_property(df, x_axis, classes, ["all"] * df.shape[0]),
            ),
            layout_wrapper(
                component=dcc.Dropdown(
                    id={"type": "x_axis_histo", "index": index},
                    value=x_axis,
                    clearable=False,
                    options=num_columns,
                ),
                css_class="dd-single",
                title="x axis",
            ),
            cluster_dropdown(
                "hg_cluster_comparison_dropdown",
                index,
                multi=True,
                clearable=True,
                value=classes,
                title="Cluster Comparison",
                css_class="dd-single",
            ),
        ]


def make_fig_property(df, x_axis, selected_clusters, clusters):
    if type(selected_clusters) == str:
        selected_clusters = [selected_clusters]

    if not selected_clusters:
        selected_clusters = sorted(set(clusters))

    props_dict = {"all": []}
    for s in selected_clusters:
        if s != "all":
            props_dict[s] = []

    for c, p in zip(clusters, df[x_axis]):
        if c != "all" and c in selected_clusters:
            props_dict[c].append(p)
        props_dict["all"].append(p)

    clusters_col = []
    x = []
    for s in selected_clusters:
        clusters_col += [s for _ in props_dict[s]]
        x += props_dict[s]

    dff = pd.DataFrame({"Clusters": clusters_col, x_axis: x})

    fig_property = px.histogram(
        dff,
        x=x_axis,
        color="Clusters",
        hover_data={
            "Clusters": False,
            x_axis: False,
        },
        color_discrete_map=cluster_colours(),
        opacity=0.5,
        histnorm="probability density",
    )

    fig_property.update_layout(
        hovermode="x unified",
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        barmode="overlay",
        yaxis=dict(
            tickformat=".2%",
        ),
    )

    return fig_property
