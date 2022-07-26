import re

import dash
import plotly.express as px

from dash import Output, Input, State, ctx, ALL, html, dcc
import dash_daq as daq
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from dashapp.tabs import Tab
from dashapp.utils.layouts import layout_wrapper, cluster_dropdown
from dashapp.utils.dcc import dropdown_regex
from dashapp.utils.dataframe import get_numeric_columns


class Cluster(Tab):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            ServersideOutput("clusters_column_store", "data"),
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
            log=True,
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
            dash_logger,
        ):
            if ctx.triggered_id in ("data_frame_store", "clusters_reset-button"):
                if ctx.triggered_id == "clusters_reset-button":
                    dash_logger.info(
                        color="green",
                        title="Success",
                        message=f"The clusters were reset successfully!",
                        autoClose=5000,
                    )

                return df_to_store(Cluster.initialize(df_from_store(df)))
            if ctx.triggered_id == "cluster-button":
                return df_to_store(
                    Cluster.create_by_input(
                        df_from_store(df),
                        features,
                        n_clusters,
                        df_from_store(kmeans_col),
                        dash_logger,
                    )
                )
            if selected_data and selected_data[0] and selected_data[0]["points"]:
                return df_to_store(
                    Cluster.create_by_drawing(
                        selected_data,
                        df_from_store(kmeans_col),
                        cluster_id,
                        selection_mode,
                    )
                )
            return kmeans_col

        @app.callback(
            Output("cluster_feature", "options"),
            Output("cluster_feature", "value"),
            Output("cluster_feature", "search_value"),
            Input("data_frame_store", "data"),
            Input("add_by_keyword-button", "n_clicks"),
            Input("cluster_feature", "value"),
            State("feature_keyword-input", "value"),
            State("cluster_feature", "options"),
            prevent_initial_call=True,
            log=True,
        )
        def add_matching_values(df, n_clicks, features, keyword, options, dash_logger):
            df = df_from_store(df)
            if ctx.triggered_id == "data_frame_store":
                options = get_numeric_columns(df, df.columns.to_list())
                return options, None, dash.no_update
            if ctx.triggered_id == "add_by_keyword-button":
                options, features, hits = dropdown_regex(options, features, keyword)

                if keyword is None:
                    dash_logger.warning(
                        message=f"No regular expression was given.",
                        autoClose=10000,
                    )
                elif hits == 0:
                    dash_logger.warning(
                        message=f'No new features matched the regular expression r"{keyword}".',
                        autoClose=10000,
                    )
                elif hits == 1:
                    dash_logger.info(
                        message=f'One new feature matched the regular expression r"{keyword}".',
                        autoClose=5000,
                    )
                else:
                    dash_logger.info(
                        message=f'{hits} new features matched the regular expression r"{keyword}".',
                        autoClose=5000,
                    )

                return options, features, None
            if ctx.triggered_id == "cluster_feature":
                options = get_numeric_columns(df, df.columns.to_list())
                options, features, hits = dropdown_regex(options, features)
                return options, features, dash.no_update

        @app.callback(
            Output("feature_keyword-input", "value"),
            Input("cluster_feature", "search_value"),
            prevent_initial_call=True,
        )
        def sync_with_input(keyword):
            if keyword == "":
                raise PreventUpdate()
            return keyword

    @staticmethod
    def initialize(df):
        kmeans_col = ["all"] * df.shape[0]
        return kmeans_col

    @staticmethod
    def create_by_input(df, features, n_clusters, kmeans_col, dash_logger=None):
        if features is None or n_clusters is None:
            if features is None and dash_logger is not None:
                dash_logger.warning(
                    message="You have not selected any features to cluster by.",
                    autoClose=10000,
                )

            if n_clusters is None and dash_logger is not None:
                dash_logger.warning(
                    message="You have not selected the number of clusters.",
                    autoClose=10000,
                )

            return kmeans_col

        # dash_logger.info(
        #     title="Processing",
        #     message="The k-means clustering process has started.",
        #     loading=True,
        #     autoClose=False,
        #     disallowClose=True,
        # )

        columns = get_numeric_columns(df, df.columns.to_list())
        new_features = []
        for f in features:
            if " (regex)" in f:
                for c in columns:
                    if re.search(f[:-8], c) and c not in new_features:
                        new_features.append(c)
            elif f not in new_features:
                new_features.append(f)
        scaler = StandardScaler()
        scale = scaler.fit_transform(df[new_features])
        km = KMeans(n_clusters=int(n_clusters)).fit_predict(scale)
        kmeans_col = [f"c{c+1}" for c in km]

        dash_logger.info(
            color="green",
            title="Success",
            message=f"The data was clustered successfully!",
            autoClose=5000,
        )

        return kmeans_col

    @staticmethod
    def create_by_drawing(selected_data, kmeans_col, cluster_id, selection_mode):
        if selection_mode:
            for p in selected_data[0]["points"]:
                kmeans_col[p["customdata"][0]["index"]] = cluster_id
        else:
            kmeans_col = ["c2"] * len(kmeans_col)
            for p in selected_data[0]["points"]:
                kmeans_col[p["customdata"][0]["index"]] = "c1"
        return kmeans_col, None, None

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
                    "Add features by regex",
                    id="add_by_keyword-button",
                    style={"padding-top": "20"},
                ),
                html.Div(),
                html.Div(
                    [html.Button("Compute the clusters", id="cluster-button")],
                    style={
                        "padding-left": "2%",
                        "padding-top": "2%",
                        "display": "inline-block",
                    },
                ),
                html.Div(
                    [html.Button("Reset the clusters", id="clusters_reset-button")],
                    style={"display": "inline-block"},
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
