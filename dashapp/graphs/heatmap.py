import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH
from sklearn.cluster import KMeans

from dashapp.utils.layouts import layout_wrapper, delete_button
from dashapp.graphs import Graph


class Heatmap(Graph):
    @staticmethod
    def name() -> str:
        return "Heatmap"

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "heatmap", "index": MATCH}, "figure"),
            Input({"type": "heatmap_cluster_amount", "index": MATCH}, "value"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def render_heatmap(n_clusters, df):
            df = df_from_store(df)
            columns = df.columns.to_list()

            km = KMeans(n_clusters=n_clusters, random_state=42)
            km.fit(df.drop("auxiliary", axis=1))
            cluster_centers = km.cluster_centers_

            fig = px.imshow(
                cluster_centers,
                x=columns.remove("auxiliary"),
                y=[str(n + 1) for n in range(n_clusters)],
                color_continuous_scale="RdBu",
                origin="lower",
            )
            style = {"widthe": "32%", "display": "inline-block", "float": "left"}
            return fig, style

        @app.callback(
            Output({"type": "heatmap-container", "index": MATCH}, "style"),
            Input({"type": "heatmap-delete", "index": MATCH}, "n_clicks"),
            Input("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def delete_heatmap(n_clicks, df):
            return {"display": "none"}

    @staticmethod
    def create_new_layout(index, df, columns):
        return html.Div(
            [
                delete_button("heatmap-delete", index),
                dcc.Graph(
                    id={"type": "heatmap", "index": index},
                    figure=px.imshow(df, color_continuous_scale="RdBu", origin="lower"),
                ),
                layout_wrapper(
                    component=dcc.Slider(
                        min=2,
                        max=10,
                        step=1,
                        id={"type": "heatmap_cluster_amount", "index": index},
                    ),
                    title="Cluster amount",
                    style={"width": "80%"},
                ),
            ],
            id={"type": "heatmap-container", "index": index},
            style={"width": "32%", "display": "inline-block", "float": "left"},
        )
