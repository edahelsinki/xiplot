import re
import uuid

import dash
import dash_daq as daq
import dash_mantine_components as dmc
import plotly.express as px

from dash import Output, Input, State, ctx, ALL, html, dcc
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
            Output("cluster-tab-main-notify-container", "children"),
            Output("cluster-tab-compute-done", "children"),
            Input("data_frame_store", "data"),
            Input("cluster-button", "value"),
            State("cluster-tab-main-notify-container", "children"),
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
            process_id,
            done,
            selected_data,
            n_clicks,
            n_clusters,
            features,
            kmeans_col,
            cluster_id,
            selection_mode,
        ):
            if ctx.triggered_id in ("data_frame_store", "clusters_reset-button"):
                df = df_from_store(df)

                if df is None:
                    return (
                        dash.no_update,
                        dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="yellow",
                            title="Warning",
                            message="You have not yet loaded any data file.",
                            action="show",
                            autoClose=10000,
                        ),
                        dash.no_update,
                    )

                notifications = []

                if process_id != done and process_id is not None:
                    notifications.append(
                        dmc.Notification(
                            id=process_id,
                            action="hide",
                        )
                    )

                if ctx.triggered_id == "clusters_reset-button":
                    notifications.append(
                        dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="green",
                            title="Success",
                            message="The clusters were reset successfully!",
                            action="show",
                            autoClose=5000,
                        )
                    )

                return df_to_store(Cluster.initialize(df)), notifications, process_id
            if ctx.triggered_id == "cluster-button":
                notifications = []

                kmeans_col = df_to_store(
                    Cluster.create_by_input(
                        df_from_store(df),
                        features,
                        n_clusters,
                        df_from_store(kmeans_col),
                        notifications,
                        process_id,
                    )
                )

                return kmeans_col, notifications, process_id
            if selected_data and selected_data[0] and selected_data[0]["points"]:
                notification = None

                if process_id != done and process_id is not None:
                    notification = dmc.Notification(
                        id=process_id,
                        action="hide",
                    )

                return (
                    df_to_store(
                        Cluster.create_by_drawing(
                            selected_data,
                            df_from_store(kmeans_col),
                            cluster_id,
                            selection_mode,
                        )
                    ),
                    notification,
                    process_id,
                )

            notification = None

            if process_id != done and process_id is not None:
                notification = dmc.Notification(
                    id=process_id,
                    action="hide",
                )

            return kmeans_col, notification, process_id

        @app.callback(
            Output("cluster-button", "value"),
            Output("cluster-tab-compute-notify-container", "children"),
            Input("cluster-button", "n_clicks"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
            State("cluster-tab-compute-done", "children"),
            State("cluster-button", "value"),
            prevent_initial_call=True,
        )
        def compute_clusters(n_clicks, n_clusters, features, done, doing):
            if done != doing:
                return dash.no_update, dmc.Notification(
                    id=str(uuid.uuid4()),
                    color="yellow",
                    title="Warning",
                    message="The k-means clustering process has not yet finished.",
                    action="show",
                    autoClose=10000,
                )

            notifications = []

            if not Cluster.validate_cluster_params(
                features, n_clusters, notifications=notifications
            ):
                return dash.no_update, notifications

            process_id = str(uuid.uuid4())

            return process_id, dmc.Notification(
                id=process_id,
                color="blue",
                title="Processing",
                message="The k-means clustering process has started.",
                action="show",
                loading=True,
                autoClose=False,
                disallowClose=True,
            )

        @app.callback(
            Output("cluster_feature", "options"),
            Output("cluster_feature", "value"),
            Output("cluster_feature", "search_value"),
            Output("cluster-tab-regex-notify-container", "children"),
            Input("data_frame_store", "data"),
            Input("add_by_keyword-button", "n_clicks"),
            Input("cluster_feature", "value"),
            State("feature_keyword-input", "value"),
            State("cluster_feature", "options"),
            prevent_initial_call=True,
        )
        def add_matching_values(df, n_clicks, features, keyword, options):
            df = df_from_store(df)
            if ctx.triggered_id == "data_frame_store":
                options = get_numeric_columns(df, df.columns.to_list())
                return options, None, dash.no_update, None
            if ctx.triggered_id == "add_by_keyword-button":
                options, features, hits = dropdown_regex(
                    options or [], features, keyword
                )

                if keyword is None:
                    notification = dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=f"No regular expression was given.",
                        action="show",
                        autoClose=10000,
                    )
                elif hits == 0:
                    notification = dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=f'No new features matched the regular expression r"{keyword}".',
                        action="show",
                        autoClose=10000,
                    )
                elif hits == 1:
                    notification = dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="blue",
                        title="Info",
                        message=f'One new feature matched the regular expression r"{keyword}".',
                        action="show",
                        autoClose=5000,
                    )
                else:
                    notification = dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="blue",
                        title="Info",
                        message=f'{hits} new features matched the regular expression r"{keyword}".',
                        action="show",
                        autoClose=5000,
                    )

                return options, features, None, notification
            if ctx.triggered_id == "cluster_feature":
                options = get_numeric_columns(df, df.columns.to_list())
                options, features, hits = dropdown_regex(options, features)
                return options, features, dash.no_update, None

        @app.callback(
            Output("feature_keyword-input", "value"),
            Input("cluster_feature", "search_value"),
            prevent_initial_call=True,
        )
        def sync_with_input(keyword):
            if keyword == "":
                raise PreventUpdate()
            return keyword

        @app.callback(
            Output({"type": "selection_cluster_dropdown", "index": 0}, "value"),
            Output({"type": "selection_cluster_dropdown", "index": 0}, "disabled"),
            Input("cluster_selection_mode", "value"),
            State({"type": "selection_cluster_dropdown", "index": 0}, "value"),
            prevent_initial_call=True,
        )
        def pin_selection_cluster(selection_mode, selection_cluster):
            if not selection_mode:
                return "c1", True
            return selection_cluster, False

    @staticmethod
    def initialize(df):
        kmeans_col = ["all"] * df.shape[0]
        return kmeans_col

    @staticmethod
    def validate_cluster_params(
        features, n_clusters, notifications=None, process_id=None
    ):
        if features is None or n_clusters is None:
            if notifications is not None and process_id is not None:
                notifications.append(
                    dmc.Notification(
                        id=process_id,
                        action="hide",
                    )
                )

            if features is None and notifications is not None:
                notifications.append(
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message="You have not selected any features to cluster by.",
                        action="show",
                        autoClose=10000,
                    )
                )

            if n_clusters is None and notifications is not None:
                notifications.append(
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message="You have not selected the number of clusters.",
                        action="show",
                        autoClose=10000,
                    )
                )

            return False

        return True

    @staticmethod
    def create_by_input(
        df, features, n_clusters, kmeans_col, notifications=None, process_id=None
    ):
        if not Cluster.validate_cluster_params(
            features, n_clusters, notifications, process_id
        ):
            return kmeans_col

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

        notifications.append(
            dmc.Notification(
                id=process_id or str(uuid.uuid4()),
                color="green",
                title="Success",
                message=f"The data was clustered successfully!",
                action="update" if process_id else "show",
                autoClose=5000,
                disallowClose=False,
            )
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
        return kmeans_col

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
                        value=True,
                        label="replace mode/edit mode",
                    ),
                    style={"display": "inline-block"},
                ),
            ],
            id="control_clusters_content-container",
        )

    @staticmethod
    def create_layout_globals():
        return html.Div(
            [
                html.Div(
                    id="cluster-tab-main-notify-container",
                    style={"display": "none"},
                ),
                html.Div(
                    id="cluster-tab-regex-notify-container",
                    style={"display": "none"},
                ),
                html.Div(
                    id="cluster-tab-compute-notify-container",
                    style={"display": "none"},
                ),
                html.Div(id="cluster-tab-compute-done", style={"display": "none"}),
            ],
            style={"display": "none"},
        )
