import plotly.express as px

from dash import Output, Input, State, ctx, ALL, html, dcc
import dash_daq as daq
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from dashapp.tabs import Tab
from dashapp.utils.layouts import layout_wrapper, cluster_dropdown
from dashapp.utils.dcc import dropdown_multi_selection


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
            Input("clusters_reset-button", "n_clicks"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
            State("clusters_column_store", "data"),
            State({"type": "selection_cluster_dropdown", "index": 0}, "value"),
            State("cluster_selection_mode", "value"),
            prevent_initial_call=True,
        )
        def set_clusters(
            df,
            n_clicks,
            selected_data,
            m_clicks,
            n_clusters,
            features,
            kmeans_col,
            cluster_id,
            selection_mode,
        ):
            df = df_from_store(df)
            if ctx.triggered_id in ("data_frame_store", "clusters_reset-button"):
                kmeans_col = ["all"] * len(df)
                return kmeans_col, None, None
            if ctx.triggered_id == "cluster-button":
                scaler = StandardScaler()
                scale = scaler.fit_transform(df[features])
                km = KMeans(n_clusters=int(n_clusters)).fit_predict(scale)
                kmeans_col = [f"c{c+1}" for c in km]

                style = {"display": "inline"}
                message = "Clusters created!"
                return kmeans_col, style, message
            if selected_data and selected_data[0] and selected_data[0]["points"]:
                if selection_mode:
                    for p in selected_data[0]["points"]:
                        kmeans_col[p["customdata"][0]["index"]] = cluster_id
                else:
                    kmeans_col = ["c2"] * len(kmeans_col)
                    for p in selected_data[0]["points"]:
                        kmeans_col[p["customdata"][0]["index"]] = "c1"
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
            features = dropdown_multi_selection(columns, features, keyword)
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

        @app.callback(
            Output("cluster_feature", "options"),
            Input("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def update_cluster_columns(df):
            df = df_from_store(df)

            columns = df.columns.to_list()
            columns.remove("auxiliary")

            return columns

    @staticmethod
    def create_layout():
        return html.Div(
            [
                layout_wrapper(
                    component=dcc.Dropdown(
                        options=[
                            i for i in range(2, len(px.colors.qualitative.Plotly))
                        ],
                        id="cluster_amount",
                    ),
                    css_class="dd-double-right",
                    title="cluster amount",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(id="cluster_feature", multi=True),
                    css_class="dd-double-right",
                    title="features",
                ),
                layout_wrapper(
                    component=dcc.Input(id="feature_keyword-input"),
                    style={"display": "none"},
                ),
                html.Button(
                    "Add", id="add_by_keyword-button", style={"padding-top": "20"}
                ),
                html.Div(),
                html.Div(
                    [html.Button("Run", id="cluster-button")],
                    style={
                        "padding-left": "2%",
                        "padding-top": "2%",
                        "display": "inline-block",
                    },
                ),
                html.Div(
                    [html.Button("Reset", id="clusters_reset-button")],
                    style={"display": "inline-block"},
                ),
                html.Div(
                    [html.H4(id="clusters_created_message")],
                    id="clusters_created_message-container",
                    style={"display": "none"},
                ),
                html.Div(),
                cluster_dropdown(
                    "selection_cluster_dropdown", 0, True, {"margin-left": "2%"}
                ),
                layout_wrapper(
                    component=daq.ToggleSwitch(
                        id="cluster_selection_mode",
                        value=False,
                        label="replace mode/edit mode",
                    ),
                    style={"display": "inline-block"},
                ),
            ],
            id="control_clusters_content-container",
        )
