from sre_parse import State

from matplotlib.pyplot import cla
from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import os


data_files = [f for f in os.listdir(
    "data") if os.path.isfile(os.path.join("data", f))]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.H3(children="Choose a data file"),
    dcc.Dropdown(data_files, data_files[0], id="data_files", clearable=False),
    html.Button("Load the data file", id="submit-button",
                n_clicks=0, className="btn btn-primary"),
    html.H3(id="chosen_data_file")
])


@app.callback(
    Output("chosen_data_file", "children"),
    Input("submit-button", "n_clicks"),
    State("data_files", "value")
)
def choose_data_file(n_clicks, filename):
    return f"Data file: {filename}"


def start():
    app.run_server()
