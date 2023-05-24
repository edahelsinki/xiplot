import pandas as pd
from dash import MATCH, Input, Output, html


def plugin_load():
    def read(data):
        print("Reading test data")
        return pd.DataFrame({"x": [1, 2, 3]})

    return read, ".test"


def plugin_write():
    def write(df, file):
        print("Writing test data")

    return write, ".test", "example/none"


def create_global():
    return html.Div(
        [
            html.Button(
                ["Test Plugin"], id={"type": "test_plugin_button", "index": 0}
            ),
            html.Span(
                ["No clicks"], id={"type": "test_plugin_counter", "index": 0}
            ),
        ],
        id="test-plugin-global",
    )


def register_callbacks(app, df_from_store, df_to_store):
    @app.callback(
        Output({"type": "test_plugin_counter", "index": MATCH}, "children"),
        Input({"type": "test_plugin_button", "index": MATCH}, "n_clicks"),
    )
    def counter(num):
        return f"{num} clicks"

    print("The test-plugin has registered a callback")


class Plot:
    @classmethod
    def name(cls) -> str:
        return "  TEST PLUGIN"

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"index": MATCH, "type": "test_counter"}, "children"),
            Input({"index": MATCH, "type": "test_button"}, "n_clicks"),
        )
        def counter(num):
            return f"{num} clicks"

        print("The test-plugin plot has registered a callback")

    @staticmethod
    def create_new_layout(index, df, columns, config=dict()):
        return html.Div(
            [
                html.Button(
                    ["Test Plot"], id={"index": index, "type": "test_button"}
                ),
                html.Span(
                    ["No clicks"], id={"index": index, "type": "test_counter"}
                ),
            ]
        )
