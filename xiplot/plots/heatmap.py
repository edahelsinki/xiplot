import dash
import plotly.express as px
import jsonschema

from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate
from xiplot.utils.components import DeleteButton, PdfButton, PlotData

from xiplot.utils.layouts import layout_wrapper
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.regex import dropdown_regex, get_columns_by_regex
from xiplot.utils.embedding import add_pca_columns_to_df
from xiplot.plots import APlot


class Heatmap(APlot):
    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        PdfButton.register_callback(app, {"type": "heatmap"})

        @app.callback(
            Output({"type": "heatmap", "index": MATCH}, "figure"),
            Input({"type": "heatmap_cluster_amount", "index": MATCH}, "value"),
            Input({"type": "heatmap_feature_dropdown", "index": MATCH}, "value"),
            Input("data_frame_store", "data"),
            Input("pca_column_store", "data"),
            Input("plotly-template", "data"),
            prevent_initial_call=False,
        )
        def tmp(n_clusters, features, df, pca_cols, template):
            # Try branch for testing
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except:
                pass

            return Heatmap.render(
                n_clusters, features, df_from_store(df), pca_cols, template
            )

        @app.callback(
            Output({"type": "heatmap_feature_dropdown", "index": MATCH}, "options"),
            Output({"type": "heatmap_feature_dropdown", "index": MATCH}, "value"),
            Output(
                {"type": "heatmap_feature_dropdown", "index": MATCH}, "search_value"
            ),
            Input("data_frame_store", "data"),
            Input("pca_column_store", "data"),
            Input({"type": "heatmap_regex-button", "index": MATCH}, "n_clicks"),
            Input({"type": "heatmap_feature_dropdown", "index": MATCH}, "value"),
            State({"type": "heatmap_feature_dropdown", "index": MATCH}, "options"),
            State({"type": "heatmap_feature-input", "index": MATCH}, "value"),
        )
        def add_features_by_regex(df, pca_cols, n_clicks, features, options, keyword):
            df = df_from_store(df)

            if ctx.triggered_id == "data_frame_store":
                options = get_numeric_columns(df, df.columns.to_list())
                return options, None, dash.no_update

            if (
                ctx.triggered_id == "pca_column_store"
                and "Xiplot_PCA_1" not in options
                and "Xiplot_PCA_2" not in options
            ):

                options.extend(["Xiplot_PCA_1", "Xiplot_PCA_2"])
                return options, dash.no_update, dash.no_update

            if not features:
                features = []

            if ctx.triggered_id["type"] == "heatmap_regex-button":
                options, features, hits = dropdown_regex(
                    options or [], features, keyword
                )
                return options, features, ""

            if ctx.triggered_id["type"] == "heatmap_feature_dropdown":
                options = get_numeric_columns(df, df.columns.to_list())

                if pca_cols:
                    options.extend(["Xiplot_PCA_1", "Xiplot_PCA_2"])

                options, features, hits = dropdown_regex(options, features)
                return options, features, ""

        @app.callback(
            Output({"type": "heatmap_feature-input", "index": MATCH}, "value"),
            Input({"type": "heatmap_feature_dropdown", "index": MATCH}, "search_value"),
        )
        def sync_with_input(keyword):
            if keyword == "":
                raise PreventUpdate()
            return keyword

        PlotData.register_callback(
            cls.name(),
            app,
            dict(
                clusters=Input(
                    {"type": "heatmap_cluster_amount", "index": MATCH}, "value"
                )
            ),
        )

        return [tmp]

    @staticmethod
    def render(n_clusters, features, df, pca_cols=[], template=None):
        from sklearn.cluster import KMeans

        km = KMeans(n_clusters=n_clusters, random_state=42)
        df = add_pca_columns_to_df(df, pca_cols)
        dff = df.dropna()

        features = get_columns_by_regex(dff.columns.to_list(), features)

        features = features if features else df.columns.to_list()
        features = get_numeric_columns(dff, features)

        km.fit(dff[features])

        cluster_centers = km.cluster_centers_

        fig = px.imshow(
            cluster_centers,
            x=features,
            y=[str(n + 1) for n in range(n_clusters)],
            color_continuous_scale="RdBu",
            origin="lower",
            template=template,
        )
        return fig

    @staticmethod
    def create_layout(index, df, columns, config=dict()):
        jsonschema.validate(
            instance=config,
            schema=dict(
                type="object",
                properties=dict(
                    clusters=dict(
                        type="object",
                        properties=dict(
                            amount=dict(
                                type="integer",
                                minimum=2,
                                maximum=10,
                            ),
                        ),
                    ),
                ),
            ),
        )

        try:
            n_clusters = config["clusters"]["amount"]
        except Exception:
            n_clusters = 2

        num_columns = get_numeric_columns(df, columns)
        return [
            dcc.Graph(id={"type": "heatmap", "index": index}),
            layout_wrapper(
                component=dcc.Dropdown(
                    options=num_columns,
                    multi=True,
                    id={"type": "heatmap_feature_dropdown", "index": index},
                    clearable=False,
                ),
                title="Features",
                style={"width": "80%"},
            ),
            html.Button(
                "Add features by regex",
                id={"type": "heatmap_regex-button", "index": index},
            ),
            layout_wrapper(
                component=dcc.Input(
                    id={"type": "heatmap_feature-input", "index": index}
                ),
                style={"display": "none"},
            ),
            layout_wrapper(
                component=dcc.Slider(
                    min=2,
                    max=10,
                    step=1,
                    value=n_clusters,
                    id={"type": "heatmap_cluster_amount", "index": index},
                ),
                title="Cluster amount",
                style={"width": "80%"},
            ),
        ]
