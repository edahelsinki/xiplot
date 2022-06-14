from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import os
from services.data_frame import load_auto_mpg


data_files = [f for f in os.listdir(
    "data") if os.path.isfile(os.path.join("data", f))]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.H3(children="Choose a data file"),
    dcc.Dropdown(data_files, id="data_files", clearable=False),
    html.Button("Load the data file", id="submit-button",
                n_clicks=0, className="btn btn-primary"),
    html.H3(id="chosen_data_file"),
    html.Div([
        html.H3(children="x axis"),
        dcc.Dropdown(id="x_axis", clearable=False),
        html.H3(children="y axis"),
        dcc.Dropdown(id="y_axis", clearable=False),
    ]),
    dcc.Graph(id="scatter-plot"),
])


@app.callback(
    Output("chosen_data_file", "children"),
    Output("x_axis", "options"),
    Output("y_axis", "options"),
    Input("submit-button", "n_clicks"),
    State("data_files", "value"),
    prevent_initial_call=True,
)
def choose_data_file(n_clicks, filename):
    df = load_auto_mpg(filename)
    columns = df.columns.tolist()
    return f"Data file: {filename}", columns, columns


@app.callback(
    Output("scatter-plot", "figure"),
    Input("x_axis", "value"), Input("y_axis", "value"),
    State("data_files", "value"),
    prevent_initial_call=True
)
def render_scatter(x_axis, y_axis, filename):
    df = load_auto_mpg(filename)
    fig = px.scatter(df, x=x_axis, y=y_axis)
    return fig


def start():
    # if __name__ == "__main__":
    app.run_server(debug=True)
