from xiplot.tabs import Tab
from xiplot.utils.layouts import layout_wrapper
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.embedding import get_pca_columns

from dash import html, Input, Output, State, dcc, ctx


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
            Input("embedding-button", "n_clicks"),
            State("data_frame_store", "data"),
            State("embedding_feature", "value"),
        )
        def compute_embedding(n_clicks, df, features):
            df = df_from_store(df)
            return get_pca_columns(df, features)

    def create_layout():
        return html.Div(
            [
                layout_wrapper(
                    dcc.Dropdown(id="embedding_type", options=["PCA"]),
                    css_class="dd-double-right",
                    title="Embedding type",
                ),
                layout_wrapper(
                    component=dcc.Dropdown(id="embedding_feature", multi=True),
                    css_class="dd-double-right",
                    title="Features",
                ),
                html.Button(
                    "Compute the embedding",
                    id="embedding-button",
                    className="button",
                    style={
                        "margin-left": "auto",
                        "margin-right": "auto",
                    },
                ),
            ],
            id="control-embedding-container",
        )
