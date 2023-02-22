import pandas as pd
from dash import html


def plugin_load():
    def read(data):
        print("Reading test data")
        return pd.DataFrame({"x": [1, 2, 3]})

    return read, ".test"


def plugin_plot():
    return Plot


class Plot:
    @classmethod
    def name(cls) -> str:
        return "Test_plugin_plot"

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        pass

    @staticmethod
    def create_new_layout(index, df, columns, config=dict()):
        return html.Div("Test_Plot")
