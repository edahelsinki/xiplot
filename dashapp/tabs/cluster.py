import re
import uuid
import sys

import dash
import dash_daq as daq
import dash_mantine_components as dmc
import plotly.express as px
import jsonschema

from dash import Output, Input, State, ctx, ALL, html, dcc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import CycleBreakerInput

from dashapp.tabs import Tab
from dashapp.utils.layouts import layout_wrapper, cluster_dropdown
from dashapp.utils.dcc import dropdown_regex
from dashapp.utils.dataframe import get_numeric_columns
from dashapp.utils.cluster import cluster_colours


class Cluster(Tab):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output("clusters_column_store", "data"),
            Output("cluster-tab-main-notify-container", "children"),
            Output("cluster-tab-compute-done", "children"),
            State("data_frame_store", "data"),
            Input("cluster-button", "value"),
            State("cluster-tab-compute-done", "children"),
            Input("clusters_reset-button", "n_clicks"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
            CycleBreakerInput("clusters_column_store", "data"),
            Input("clusters_column_store_reset", "children"),
        )
        def set_clusters(
            df,
            process_id,
            done,
            n_clicks,
            n_clusters,
            features,
            kmeans_col,
            reset,
        ):
            if ctx.triggered_id == "clusters_reset-button":
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
                            color="blue",
                            title="Info",
                            message="The clustering was cancelled.",
                            action="update",
                            autoClose=5000,
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

                return ["all"] * df.shape[0], notifications, process_id

            if ctx.triggered_id == "cluster-button":
                notifications = []

                try:
                    kmeans_col = Cluster.create_by_input(
                        df_from_store(df),
                        features,
                        n_clusters,
                        kmeans_col,
                        notifications,
                        process_id,
                    )
                except ImportError as err:
                    raise err
                except Exception as err:
                    notifications.append(
                        dmc.Notification(
                            id=process_id or str(uuid.uuid4()),
                            color="red",
                            title="Error",
                            message=f"The clustering failed with an internal error. Please report the following bug: {err}",
                            action="update" if process_id else "show",
                            autoClose=False,
                        )
                    )

                    return dash.no_update, notifications, process_id

                return kmeans_col, notifications, process_id

            notifications = []

            if process_id != done and process_id is not None:
                notifications.append(
                    dmc.Notification(
                        id=process_id,
                        color="blue",
                        title="Info",
                        message="The clustering was cancelled.",
                        action="update",
                        autoClose=5000,
                    )
                )

            return dash.no_update, notifications, process_id

        @app.callback(
            Output("cluster-button", "value"),
            Output("cluster-tab-compute-notify-container", "children"),
            Input("cluster-button", "n_clicks"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
            State("cluster-tab-compute-done", "children"),
            State("cluster-button", "value"),
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

            message = "The k-means clustering process has started."

            if "sklearn" not in sys.modules:
                message += " [sklearn has to first be loaded lazily]"

            return process_id, dmc.Notification(
                id=process_id,
                color="blue",
                title="Processing",
                message=message,
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
        )
        def sync_with_input(keyword):
            if keyword == "":
                raise PreventUpdate()
            return keyword

        @app.callback(
            Output("selection_cluster_dropdown", "value"),
            Output("selection_cluster_dropdown", "disabled"),
            Input("cluster_selection_mode", "value"),
            State("selection_cluster_dropdown", "value"),
        )
        def pin_selection_cluster(selection_mode, selection_cluster):
            if not selection_mode:
                return "c1", True
            return selection_cluster, False

        @app.callback(
            Output("cluster_selection_mode", "value"),
            Output("selection_cluster_dropdown", "value"),
            Output("cluster-tab-settings-notify-container", "children"),
            State("metadata_store", "data"),
            Input("metadata_session", "data"),
            State("cluster_selection_mode", "value"),
        )
        def init_from_settings(meta, meta_session, selection_mode):
            try:
                jsonschema.validate(
                    instance=meta,
                    schema=dict(
                        type="object",
                        properties=dict(
                            settings=dict(
                                type="object",
                                properties={
                                    "cluster-tab": dict(
                                        type="object",
                                        properties=dict(
                                            selection={
                                                "type": "object",
                                                "properties": dict(
                                                    mode=dict(enum=["fg-bg", "draw"]),
                                                    brush=dict(
                                                        enum=list(
                                                            cluster_colours().keys()
                                                        )
                                                    ),
                                                ),
                                                "if": dict(
                                                    properties=dict(
                                                        mode=dict(const="draw")
                                                    ),
                                                ),
                                                "then": dict(required=["brush"]),
                                            },
                                        ),
                                    ),
                                },
                            ),
                        ),
                        required=["settings"],
                    ),
                )
            except jsonschema.exceptions.ValidationError as err:
                return (
                    selection_mode,
                    dash.no_update,
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=f"Invalid cluster tab settings at meta{err.json_path[1:]}: {err.message}.",
                        action="show",
                        autoClose=10000,
                    ),
                )

            try:
                mode = meta["settings"]["cluster-tab"]["selection"]["mode"]
            except Exception:
                return selection_mode, dash.no_update, dash.no_update

            if mode == "draw":
                brush = meta["settings"]["cluster-tab"]["selection"]["brush"]

                return True, brush, dash.no_update
            else:  # mode == "fg-bg"
                return False, dash.no_update, dash.no_update

        @app.callback(
            Output("metadata_store", "data"),
            State("metadata_store", "data"),
            Input("cluster_selection_mode", "value"),
            Input("selection_cluster_dropdown", "value"),
        )
        def update_settings(meta, selection_mode, selection_cluster):
            if meta is None:
                return dash.no_update

            if not selection_mode:
                meta["settings"]["cluster-tab"] = dict(selection=dict(mode="fg-bg"))
            else:
                meta["settings"]["cluster-tab"] = dict(
                    selection=dict(mode="draw", brush=selection_cluster)
                )

            return meta

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

        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

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
    def create_layout():
        return html.Div(
            [
                layout_wrapper(
                    component=dcc.Dropdown(
                        options=[i for i in range(2, len(cluster_colours()))],
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
                    id_name="selection_cluster_dropdown",
                    value="c1",
                    disabled=True,
                    css_class="dd-double-left",
                    title="Selection Cluster",
                    style={"margin-left": "2%"},
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
                html.Div(
                    id="cluster-tab-settings-notify-container",
                    style={"display": "none"},
                ),
            ],
            style={"display": "none"},
        )
