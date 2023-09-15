import sys
import uuid

import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, State, ctx, dcc, html
from dash_extensions.enrich import CycleBreakerInput

from xiplot.tabs import Tab
from xiplot.utils.auxiliary import (
    CLUSTER_COLUMN_NAME,
    decode_aux,
    encode_aux,
    merge_df_aux,
)
from xiplot.utils.cluster import KMeans, cluster_colours
from xiplot.utils.components import ClusterDropdown, ColumnDropdown, FlexRow
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.layouts import layout_wrapper
from xiplot.utils.regex import get_columns_by_regex


class Cluster(Tab):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output("auxiliary_store", "data"),
            Output("cluster-tab-main-notify-container", "children"),
            Output("cluster-tab-compute-done", "children"),
            State("data_frame_store", "data"),
            State("auxiliary_store", "data"),
            Input("cluster-button", "value"),
            State("cluster-tab-compute-done", "children"),
            Input("clusters_reset-button", "n_clicks"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
        )
        def set_clusters(
            df,
            aux,
            process_id,
            done,
            n_clicks,
            n_clusters,
            features,
        ):
            if ctx.triggered_id == "clusters_reset-button":
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

                df = df_from_store(df)
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

                aux = decode_aux(aux)
                if CLUSTER_COLUMN_NAME in aux:
                    del aux[CLUSTER_COLUMN_NAME]
                    return encode_aux(aux), notifications, process_id
                return dash.no_update, notifications, process_id

            if ctx.triggered_id == "cluster-button":
                notifications = []

                try:
                    aux = decode_aux(aux)
                    df2 = merge_df_aux(df_from_store(df), aux)
                    kmeans_col = Cluster.create_by_input(
                        df2,
                        features,
                        n_clusters,
                        notifications,
                        process_id,
                    )

                    if kmeans_col != dash.no_update:
                        aux[CLUSTER_COLUMN_NAME] = pd.Categorical(kmeans_col)
                        return encode_aux(aux), notifications, process_id
                except ImportError as err:
                    raise err
                except Exception as err:
                    notifications.append(
                        dmc.Notification(
                            id=process_id or str(uuid.uuid4()),
                            color="red",
                            title="Error",
                            message=(
                                "The clustering failed with an internal"
                                " error. Please report the following bug:"
                                f" {err}"
                            ),
                            action="update" if process_id else "show",
                            autoClose=False,
                        )
                    )
                return dash.no_update, notifications, process_id

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
                    message=(
                        "The k-means clustering process has not yet finished."
                    ),
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
                message += " [Loading scikit-learn]"

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

        ColumnDropdown.register_callback(
            app,
            "cluster_feature",
            df_from_store,
            numeric=True,
            regex_button_id="add_by_keyword-button",
            regex_input_id="feature_keyword-input",
        )

        @app.callback(
            Output("selection_cluster_dropdown", "value"),
            Output("selection_cluster_dropdown", "disabled"),
            Input("cluster_selection_mode", "value"),
        )
        def pin_selection_cluster(selection_mode):
            if not selection_mode:
                return "c1", True
            return dash.no_update, False

        @app.callback(
            Output("cluster-tab-settings-session", "children"),
            Output("cluster_selection_mode", "value"),
            Output("selection_cluster_dropdown", "value"),
            Output("cluster-tab-settings-notify-container", "children"),
            CycleBreakerInput("metadata_store", "data"),
            State("cluster-tab-settings-session", "children"),
        )
        def init_from_settings(meta, last_meta_session):
            if meta is None:
                return (
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                )

            if meta["session"] == last_meta_session:
                return (
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                )

            import jsonschema

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
                                                    mode=dict(
                                                        enum=["fg-bg", "draw"]
                                                    ),
                                                    brush=dict(
                                                        enum=list(
                                                            cluster_colours().keys()  # noqa: 501
                                                        )
                                                    ),
                                                ),
                                                "if": dict(
                                                    properties=dict(
                                                        mode=dict(const="draw")
                                                    ),
                                                ),
                                                "then": dict(
                                                    required=["brush"]
                                                ),
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
                    meta["session"],
                    dash.no_update,
                    dash.no_update,
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=(
                            "Invalid cluster tab settings at"
                            f" meta{err.json_path[1:]}: {err.message}."
                        ),
                        action="show",
                        autoClose=10000,
                    ),
                )

            try:
                mode = meta["settings"]["cluster-tab"]["selection"]["mode"]
            except Exception:
                return (
                    meta["session"],
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                )

            if mode == "draw":
                brush = meta["settings"]["cluster-tab"]["selection"]["brush"]

                return meta["session"], ["edit"], brush, dash.no_update
            else:  # mode == "fg-bg"
                return meta["session"], None, dash.no_update, dash.no_update

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
                meta["settings"]["cluster-tab"] = dict(
                    selection=dict(mode="fg-bg")
                )
            else:
                meta["settings"]["cluster-tab"] = dict(
                    selection=dict(mode="draw", brush=selection_cluster)
                )

            return meta

        ClusterDropdown.register_callbacks(
            app, "selection_cluster_dropdown", True
        )

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
                        message=(
                            "You have not selected any features to cluster by."
                        ),
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
                        message=(
                            "You have not selected the number of clusters."
                        ),
                        action="show",
                        autoClose=10000,
                    )
                )

            return False

        return True

    @staticmethod
    def create_by_input(
        df,
        features,
        n_clusters,
        notifications=None,
        process_id=None,
    ):
        if not Cluster.validate_cluster_params(
            features, n_clusters, notifications, process_id
        ):
            return dash.no_update

        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import StandardScaler

        scaler = StandardScaler()
        imputer = SimpleImputer(strategy="mean")

        columns = get_numeric_columns(df)
        new_features = get_columns_by_regex(columns, features)
        x = scaler.fit_transform(df[new_features])
        x = imputer.fit_transform(x)

        km = KMeans(n_clusters=int(n_clusters)).fit_predict(x)
        kmeans_col = [f"c{c+1}" for c in km]

        notifications.append(
            dmc.Notification(
                id=process_id or str(uuid.uuid4()),
                color="green",
                title="Success",
                message="The data was clustered successfully!",
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
                FlexRow(
                    layout_wrapper(
                        component=FlexRow(
                            ColumnDropdown(id="cluster_feature", multi=True),
                            html.Button(
                                "Add features by regex",
                                id="add_by_keyword-button",
                                className="button",
                            ),
                        ),
                        css_class="stretch",
                        title="Features",
                    ),
                    layout_wrapper(
                        component=FlexRow(
                            dcc.Dropdown(
                                options=[
                                    i for i in range(2, len(cluster_colours()))
                                ],
                                value=3,
                                clearable=False,
                                id="cluster_amount",
                            ),
                            html.Button(
                                "Compute clusters",
                                id="cluster-button",
                                className="button",
                            ),
                        ),
                        css_class="stretch",
                        title="Number of clusters",
                    ),
                ),
                layout_wrapper(
                    component=dcc.Input(id="feature_keyword-input"),
                    style={"display": "none"},
                ),
                html.Br(),
                FlexRow(
                    dcc.Checklist(
                        [dict(label="Cluster edit mode", value="edit")],
                        id="cluster_selection_mode",
                        labelClassName="button",
                        inline=True,
                    ),
                    layout_wrapper(
                        component=ClusterDropdown(
                            id="selection_cluster_dropdown",
                            value="c1",
                            disabled=True,
                        ),
                        css_class="dash-dropdown",
                        title="Select cluster",
                    ),
                    html.Button(
                        "Remove clusters",
                        id="clusters_reset-button",
                        className="button",
                    ),
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
                html.Div(
                    id="cluster-tab-compute-done", style={"display": "none"}
                ),
                html.Div(
                    id="cluster-tab-settings-notify-container",
                    style={"display": "none"},
                ),
                html.Div(
                    id="cluster-tab-settings-session",
                    style={"display": "none"},
                ),
            ],
            style={"display": "none"},
        )
