import dash
import plotly.express as px
import jsonschema

from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate

from xiplot.utils.layouts import layout_wrapper, delete_button
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.regex import dropdown_regex, get_columns_by_regex
from xiplot.plots import Plot


class Heatmap(Plot):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "heatmap", "index": MATCH}, "figure"),
            Input({"type": "heatmap_cluster_amount", "index": MATCH}, "value"),
            Input({"type": "heatmap_feature_dropdown", "index": MATCH}, "value"),
            Input("data_frame_store", "data"),
        )
        def tmp(n_clusters, features, df):
            # Try branch for testing
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except:
                pass

            return Heatmap.render(n_clusters, features, df_from_store(df))

        @app.callback(
            Output({"type": "heatmap_feature_dropdown", "index": MATCH}, "options"),
            Output({"type": "heatmap_feature_dropdown", "index": MATCH}, "value"),
            Output(
                {"type": "heatmap_feature_dropdown", "index": MATCH}, "search_value"
            ),
            Input("data_frame_store", "data"),
            Input({"type": "heatmap_regex-button", "index": MATCH}, "n_clicks"),
            Input({"type": "heatmap_feature_dropdown", "index": MATCH}, "value"),
            State({"type": "heatmap_feature_dropdown", "index": MATCH}, "options"),
            State({"type": "heatmap_feature-input", "index": MATCH}, "value"),
        )
        def add_features_by_regex(df, n_clicks, features, options, keyword):
            df = df_from_store(df)
            if ctx.triggered_id == "data_frame_store":
                options = get_numeric_columns(df, df.columns.to_list())
                return options, None, dash.no_update

            if not features:
                features = []

            if ctx.triggered_id["type"] == "heatmap_regex-button":
                options, features, hits = dropdown_regex(
                    options or [], features, keyword
                )
                return options, features, ""

            if ctx.triggered_id["type"] == "heatmap_feature_dropdown":
                options = get_numeric_columns(df, df.columns.to_list())
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

        @app.callback(
            output=dict(
                meta=Output("metadata_store", "data"),
            ),
            inputs=[
                State("metadata_store", "data"),
                Input({"type": "heatmap_cluster_amount", "index": ALL}, "value"),
            ],
            prevent_initial_call=False,
        )
        def update_settings(meta, n_clusters):
            if meta is None:
                return dash.no_update

            for (n_clusters,) in zip(*ctx.args_grouping[1 : 1 + 1]):
                if not n_clusters["triggered"]:
                    continue

                index = n_clusters["id"]["index"]
                n_clusters = n_clusters["value"]

                meta["plots"][index] = dict(
                    type=Heatmap.name(), clusters=dict(amount=n_clusters)
                )

            return dict(meta=meta)

        return [tmp, update_settings]

    @staticmethod
    def render(n_clusters, features, df):
        from sklearn.cluster import KMeans

        km = KMeans(n_clusters=n_clusters, random_state=42)
        dff = df.dropna()

        features = get_columns_by_regex(
            get_numeric_columns(dff, dff.columns.to_list()), features
        )
        km.fit(dff[features])

        cluster_centers = km.cluster_centers_

        fig = px.imshow(
            cluster_centers,
            x=features,
            y=[str(n + 1) for n in range(n_clusters)],
            color_continuous_scale="RdBu",
            origin="lower",
        )
        return fig

    @staticmethod
    def create_new_layout(index, df, columns, config=dict()):
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
        return html.Div(
            [
                delete_button("plot-delete", index),
                dcc.Graph(
                    id={"type": "heatmap", "index": index},
                    figure=Heatmap.render(n_clusters, num_columns, df),
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        options=num_columns,
                        multi=True,
                        id={"type": "heatmap_feature_dropdown", "index": index},
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
            ],
            id={"type": "heatmap-container", "index": index},
            className="plots",
        )
