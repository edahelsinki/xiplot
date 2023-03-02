import pandas as pd
from dash import html


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
    return html.Div("TEST PLUGIN", style={"display": "none"})


def register_callbacks(app, df_from_store, df_to_store):
    pass


class Plot:
    @classmethod
    def name(cls) -> str:
        return "  TEST PLUGIN"

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        pass

    @staticmethod
    def create_new_layout(index, df, columns, config=dict()):
        return html.Div("Test_Plot")
