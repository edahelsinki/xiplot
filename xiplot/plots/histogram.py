import dash
import jsonschema
import pandas as pd
import plotly.express as px
from dash import ALL, MATCH, Input, Output, State, ctx, dcc
from dash.exceptions import PreventUpdate

from xiplot.plots import APlot
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.components import PdfButton, PlotData
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.embedding import add_pca_columns_to_df
from xiplot.utils.layouts import cluster_dropdown, layout_wrapper


class Histogram(APlot):
    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        PdfButton.register_callback(app, {"type": "histogram"})

        @app.callback(
            Output({"type": "histogram", "index": MATCH}, "figure"),
            Input({"type": "x_axis_histo", "index": MATCH}, "value"),
            Input(
                {"type": "hg_cluster_comparison_dropdown", "index": MATCH},
                "value",
            ),
            Input("clusters_column_store", "data"),
            Input("data_frame_store", "data"),
            Input("pca_column_store", "data"),
            Input("plotly-template", "data"),
            prevent_initial_call=False,
        )
        def tmp(
            x_axis, selected_clusters, kmeans_col, df, pca_cols, template=None
        ):
            # Try branch for testing
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except Exception:
                pass

            return Histogram.render(
                x_axis,
                selected_clusters,
                kmeans_col,
                df_from_store(df),
                pca_cols,
                template,
            )

        PlotData.register_callback(
            cls.name(),
            app,
            (
                Input({"type": "x_axis_histo", "index": ALL}, "value"),
                Input(
                    {"type": "hg_cluster_comparison_dropdown", "index": ALL},
                    "value",
                ),
            ),
            lambda i: dict(
                axes=dict(x=i[0]), groupby="Clusters", classes=i[1] or []
            ),
        )

        @app.callback(
            output=dict(
                histogram_x=Output(
                    {"type": "x_axis_histo", "index": ALL}, "options"
                ),
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

        return [tmp]

    @staticmethod
    def render(
        x_axis, selected_clusters, kmeans_col, df, pca_cols=[], template=None
    ):
        if len(kmeans_col) == df.shape[0]:
            df["Clusters"] = kmeans_col

        df = add_pca_columns_to_df(df, pca_cols)

        fig = make_fig_property(
            df, x_axis, selected_clusters, kmeans_col, template
        )

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

        _groupby = config.get("groupby", "Clusters")  # noqa: F841
        classes = config.get("classes", [])

        return [
            dcc.Graph(
                id={"type": "histogram", "index": index},
                config={"displaylogo": False, "responsive": True},
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


def make_fig_property(df, x_axis, selected_clusters, clusters, template=None):
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
        template=template,
    )

    fig_property.update_layout(
        hovermode="x unified",
        showlegend=False,
        barmode="overlay",
        yaxis=dict(
            tickformat=".2%",
        ),
    )

    return fig_property
