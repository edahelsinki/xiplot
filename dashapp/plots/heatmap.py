import dash
import plotly.express as px
import jsonschema

from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import layout_wrapper, delete_button
from dashapp.utils.dataframe import get_numeric_columns
from dashapp.plots import Plot


class Heatmap(Plot):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "heatmap", "index": MATCH}, "figure"),
            Input({"type": "heatmap_cluster_amount", "index": MATCH}, "value"),
            State("data_frame_store", "data"),
        )
        def tmp(n_clusters, df):
            return Heatmap.render(n_clusters, df_from_store(df))

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

    @staticmethod
    def render(n_clusters, df):
        from sklearn.cluster import KMeans

        df = df.dropna()
        columns = df.columns.to_list()
        num_columns = get_numeric_columns(df, columns)

        km = KMeans(n_clusters=n_clusters, random_state=42)
        km.fit(df[num_columns])

        cluster_centers = km.cluster_centers_

        fig = px.imshow(
            cluster_centers,
            x=num_columns,
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
                    figure=Heatmap.render(n_clusters, df),
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
