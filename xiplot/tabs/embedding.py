import sys
import uuid
import dash

from dash import html, Input, Output, State, dcc, ctx

import dash_mantine_components as dmc

from xiplot.tabs import Tab
from xiplot.utils.components import FlexRow
from xiplot.utils.layouts import layout_wrapper
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.embedding import get_pca_columns


class Embedding(Tab):
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output("embedding_feature", "options"),
            Input("data_frame_store", "data"),
        )
        def initialize_dropdown(df):
            df = df_from_store(df)

            options = get_numeric_columns(df, df.columns.to_list())
            return options

        @app.callback(
            Output("pca_column_store", "data"),
            Output("embedding-tab-main-notify-container", "children"),
            Output("embedding-tab-compute-done", "children"),
            Input("embedding-button", "value"),
            State("data_frame_store", "data"),
            State("embedding_feature", "value"),
        )
        def compute_embedding(process_id, df, features):
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

            try:
                pca_cols = get_pca_columns(df, features)

                notifications.append(
                    dmc.Notification(
                        id=process_id or str(uuid.uuid4()),
                        color="green",
                        title="Success",
                        message=f"The data was embedded successfully!",
                        action="update" if process_id else "show",
                        autoClose=5000,
                        disallowClose=False,
                    )
                )

            except ImportError as err:
                raise err

            except Exception as err:
                notifications.append(
                    dmc.Notification(
                        id=process_id or str(uuid.uuid4()),
                        color="red",
                        title="Error",
                        message=f"The embedding failed with an internal error. Please report the following bug: {err}",
                        action="update" if process_id else "show",
                        autoClose=False,
                    )
                )

                return (dash.no_update, notifications, process_id)

            return pca_cols, notifications, process_id

        @app.callback(
            Output("embedding-button", "value"),
            Output("embedding-tab-compute-notify-container", "children"),
            Input("embedding-button", "n_clicks"),
            State("embedding_type", "value"),
            State("embedding_feature", "value"),
            State("embedding-tab-compute-done", "children"),
            State("embedding-button", "value"),
        )
        def compute_embeddings(n_clicks, embedding_type, features, done, doing):
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

            if not Embedding.validate_embedding_params(
                embedding_type, features, notifications=notifications
            ):
                return dash.no_update, notifications

            process_id = str(uuid.uuid4())

            message = "The embedding process has started."

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

    @staticmethod
    def validate_embedding_params(
        embedding_type, features, notifications=None, process_id=None
    ):
        if features is None:
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
                        message="You have not selected any features to embed by.",
                        action="show",
                        autoClose=10000,
                    )
                )

            if embedding_type is None and notifications is not None:
                notifications.append(
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message="You have not selected embedding type.",
                        action="show",
                        autoClose=10000,
                    )
                )

            return False

        if len(features) < 2 and embedding_type == "PCA":
            if notifications is not None and process_id is not None:
                notifications.append(
                    dmc.Notification(
                        id=process_id,
                        action="hide",
                    )
                )

            if notifications is not None:
                notifications.append(
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message="You must select at least two features",
                        action="show",
                        autoClose=10000,
                    )
                )

            return False

        return True

    @staticmethod
    def create_layout():
        return FlexRow(
            layout_wrapper(
                dcc.Dropdown(
                    id="embedding_type", options=["PCA"], value="PCA", clearable=False
                ),
                css_class="dash-dropdown",
                title="Embedding type",
            ),
            layout_wrapper(
                component=dcc.Dropdown(id="embedding_feature", multi=True),
                css_class="dash-dropdown",
                title="Features",
            ),
            html.Button(
                "Compute the embedding",
                id="embedding-button",
                className="button",
            ),
            id="control-embedding-container",
        )

    @staticmethod
    def create_layout_globals():
        return html.Div(
            [
                html.Div(
                    id="embedding-tab-main-notify-container",
                    style={"display": "none"},
                ),
                html.Div(
                    id="embedding-tab-compute-notify-container",
                    style={"display": "none"},
                ),
                html.Div(id="embedding-tab-compute-done", style={"display": "none"}),
            ],
            style={"display": "none"},
        )
