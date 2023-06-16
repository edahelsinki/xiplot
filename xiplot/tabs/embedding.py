import sys
import uuid

import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, dcc, html

from xiplot.tabs import Tab
from xiplot.utils.auxiliary import decode_aux, encode_aux, merge_df_aux
from xiplot.utils.components import ColumnDropdown, FlexRow
from xiplot.utils.layouts import layout_wrapper
from xiplot.utils.regex import get_columns_by_regex


def get_pca_columns(df, features):
    from sklearn.decomposition import PCA
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler

    x = df[features]
    x = StandardScaler().fit_transform(x)

    mean_imputer = SimpleImputer(strategy="mean")
    x = mean_imputer.fit_transform(x)

    pca = PCA(n_components=2)
    pca.fit(x)
    return pca.transform(x)


class Embedding(Tab):
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output("auxiliary_store", "data"),
            Output("embedding-tab-main-notify-container", "children"),
            Output("embedding-tab-compute-done", "children"),
            Input("embedding-button", "value"),
            State("data_frame_store", "data"),
            State("auxiliary_store", "data"),
            State("embedding_feature", "value"),
            State("embedding_type", "value"),
        )
        def compute_embedding(process_id, df, aux, features, embedding_type):
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
            aux = decode_aux(aux)
            columns = ColumnDropdown.get_columns(df, aux, numeric=True)
            features = get_columns_by_regex(columns, features)

            notifications = []
            if not Embedding.validate_embedding_params(
                embedding_type, features, notifications, process_id
            ):
                return dash.no_update, notifications, process_id

            try:
                pca_cols = get_pca_columns(merge_df_aux(df, aux), features)
                aux["Xiplot_PCA_1"] = pca_cols[:, 0]
                aux["Xiplot_PCA_2"] = pca_cols[:, 1]

                notifications.append(
                    dmc.Notification(
                        id=process_id or str(uuid.uuid4()),
                        color="green",
                        title="Success",
                        message="The data was embedded successfully!",
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
                        message=(
                            "The embedding failed with an internal error."
                            f" Please report the following bug: {err}"
                        ),
                        action="update" if process_id else "show",
                        autoClose=False,
                    )
                )

                return (dash.no_update, notifications, process_id)

            return encode_aux(aux), notifications, process_id

        @app.callback(
            Output("embedding-button", "value"),
            Output("embedding-tab-compute-notify-container", "children"),
            Input("embedding-button", "n_clicks"),
            State("embedding_type", "value"),
            State("embedding_feature", "value"),
            State("embedding-tab-compute-done", "children"),
            State("embedding-button", "value"),
        )
        def compute_embeddings(
            n_clicks, embedding_type, features, done, doing
        ):
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

        ColumnDropdown.register_callback(
            app,
            "embedding_feature",
            df_from_store,
            numeric=True,
            regex_button_id="embedding-regex-button",
            regex_input_id="embedding-regex-input",
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
                        message=(
                            "You have not selected any features to embed by."
                        ),
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
                    id="embedding_type",
                    options=["PCA"],
                    value="PCA",
                    clearable=False,
                ),
                css_class="dash-dropdown",
                title="Embedding type",
            ),
            layout_wrapper(
                component=ColumnDropdown(id="embedding_feature", multi=True),
                css_class="dash-dropdown",
                title="Features",
            ),
            dcc.Input(id="embedding-regex-input", style={"display": "none"}),
            html.Button(
                "Add features by regex",
                id="embedding-regex-button",
                className="button",
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
                html.Div(
                    id="embedding-tab-compute-done", style={"display": "none"}
                ),
            ],
            style={"display": "none"},
        )
