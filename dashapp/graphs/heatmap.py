import plotly.express as px

from dash import html, dcc, Output, Input, MATCH, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import layout_wrapper, delete_button
from dashapp.utils.dataframe import get_numeric_columns
from dashapp.graphs import Graph


class Heatmap(Graph):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "heatmap", "index": MATCH}, "figure"),
            Input({"type": "heatmap_cluster_amount", "index": MATCH}, "value"),
            Input("data_frame_store", "data"),
        )
        def tmp(n_clusters, df):
            if ctx.triggered_id == "data_frame_store":
                raise PreventUpdate()

            return Heatmap.render(n_clusters, df_from_store(df))

    @staticmethod
    def render(n_clusters, df):
        from sklearn.cluster import KMeans

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
    def create_new_layout(index, df, columns):
        return html.Div(
            [
                delete_button("plot-delete", index),
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
            className="graphs",
        )
