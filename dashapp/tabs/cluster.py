import plotly.express as px

from dash import Output, Input, State, ctx, ALL, html, dcc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from dashapp.tabs import Tab
from dashapp.utils.layouts import layout_wrapper


class ClusterTab(Tab):
    @staticmethod
    def name() -> str:
        return "Clusters"

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            ServersideOutput("clusters_column_store", "data"),
            Output("clusters_created_message-container", "style"),
            Output("clusters_created_message", "children"),
            Input("data_frame_store", "data"),
            Input("cluster-button", "n_clicks"),
            Input({"type": "scatterplot", "index": ALL}, "selectedData"),
            State("cluster_amount", "value"),
            State("data_frame_store", "data"),
            State("clusters_column_store", "data"),
            State("selection_cluster_dropdown", "value"),
            prevent_initial_call=True,
        )
        def set_clusters(
            df, n_clicks, selected_data, n_clusters, features, kmeans_col, cluster_id
        ):
            df = df_from_store(df)
            if ctx.triggered_id == "data_frame_store":
                kmeans_col = ["bg"] * len(df)
                return kmeans_col, None, None
            if ctx.triggered_id == "cluster-button":
                scaler = StandardScaler()
                scale = scaler.fit_transform(df[features])
                km = KMeans(n_clusters=int(n_clusters)).fit_predict(scale)
                kmeans_col = [f"c{c+1}" for c in km]

                style = {"display": "inline"}
                message = "Clusters created!"
                return kmeans_col, style, message
            if kmeans_col is None:
                kmeans_col = ["bg"] * len(df)
            for p in selected_data[0]["points"]:
                kmeans_col[p["customdata"][0]["index"]] = cluster_id
            return kmeans_col, None, None

        @app.callback(
            Output("cluster_feature", "value"),
            Input("add_by_keyword-button", "n_clicks"),
            State("data_frame_store", "data"),
            State("feature_keyword-input", "value"),
            State("cluster_feature", "value"),
            prevent_initial_call=True,
        )
        def add_matching_values(n_clicks, df, keyword, features):
            df = df_from_store(df)
            columns = df.columns.to_list()
            if not features:
                features = []
            for column in columns:
                if keyword in column and column not in features:
                    features.append(column)
            return features

        @app.callback(
            Output("feature_keyword-input", "value"),
            Input("cluster_feature", "search_value"),
            prevent_initial_call=True,
        )
        def sync_with_input(keyword):
            if not keyword:
                raise PreventUpdate()
            return keyword

    @staticmethod
    def create_layout():
        return html.Div(
            [
                layout_wrapper(
                    component=dcc.Dropdown(
                        options=[i for i in range(2, 11)], id="cluster_amount"
                    ),
                    title="cluster amount",
                    style={
                        "width": "23%",
                        "display": "inline-block",
                        "padding-left": "2%",
                    },
                ),
                layout_wrapper(
                    component=dcc.Dropdown(id="cluster_feature", multi=True),
                    title="features",
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "padding-left": "2%",
                    },
                ),
                layout_wrapper(
                    component=dcc.Input(id="feature_keyword-input"),
                    style={"display": "none"},
                ),
                html.Button(
                    "Add", id="add_by_keyword-button", style={"padding-top": "20"}
                ),
                html.Div(
                    [html.Button("Run", id="cluster-button")],
                    style={"padding-left": "2%", "padding-top": "2%"},
                ),
                html.Div(
                    [html.H4(id="clusters_created_message")],
                    id="clusters_created_message-container",
                    style={"display": "none"},
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id="selection_cluster_dropdown",
                        clearable=False,
                        value="c1",
                        options=[
                            {
                                "label": html.Div(
                                    [
                                        html.Div(
                                            style={
                                                "width": 20,
                                                "height": 20,
                                                "display": "inline-block",
                                                "background-color": px.colors.qualitative.Plotly[
                                                    0
                                                ],
                                            }
                                        ),
                                        html.Div(
                                            "background",
                                            style={
                                                "display": "inline-block",
                                                "padding-left": 10,
                                            },
                                        ),
                                    ]
                                ),
                                "value": "bg",
                            }
                        ]
                        + [
                            {
                                "label": html.Div(
                                    [
                                        html.Div(
                                            style={
                                                "width": 20,
                                                "height": 20,
                                                "display": "inline-block",
                                                "background-color": c,
                                            }
                                        ),
                                        html.Div(
                                            f"cluster #{i+1}",
                                            style={
                                                "display": "inline-block",
                                                "padding-left": 10,
                                            },
                                        ),
                                    ]
                                ),
                                "value": f"c{i+1}",
                            }
                            for i, c in enumerate(px.colors.qualitative.Plotly[1:])
                        ],
                    ),
                    title="Selection Cluster:",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id="comparison_cluster_dropdown",
                        clearable=False,
                        value="bg",
                        options=[
                            {
                                "label": html.Div(
                                    [
                                        html.Div(
                                            style={
                                                "width": 20,
                                                "height": 20,
                                                "display": "inline-block",
                                                "background-color": px.colors.qualitative.Plotly[
                                                    0
                                                ],
                                            }
                                        ),
                                        html.Div(
                                            "background",
                                            style={
                                                "display": "inline-block",
                                                "padding-left": 10,
                                            },
                                        ),
                                    ]
                                ),
                                "value": "bg",
                            }
                        ]
                        + [
                            {
                                "label": html.Div(
                                    [
                                        html.Div(
                                            style={
                                                "width": 20,
                                                "height": 20,
                                                "display": "inline-block",
                                                "background-color": c,
                                            }
                                        ),
                                        html.Div(
                                            f"cluster #{i+1}",
                                            style={
                                                "display": "inline-block",
                                                "padding-left": 10,
                                            },
                                        ),
                                    ]
                                ),
                                "value": f"c{i+1}",
                            }
                            for i, c in enumerate(px.colors.qualitative.Plotly[1:])
                        ],
                    ),
                    title="Comparison Cluster:",
                ),
            ],
            id="control_clusters_content-container",
        )
