from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import os
from services.data_frame import load_auto_mpg, read_data_file
#from data_frame import load_auto_mpg, read_data_file


# List of all the files in the directory "data"
data_files = [f for f in os.listdir(
    "data") if os.path.isfile(os.path.join("data", f))]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.Div([
        html.H1("Dash App 2022")
    ], style={"text-align": "center", "margin": 20}),
    html.Div([
        html.Div([
            html.Div([
                html.H5(children="x axis (scatter)"),
            ], style={"padding-top": 8}),
            dcc.Dropdown(id="x_axis", clearable=False), ],
            style={"width": "45%", "display": "inline-block", "margin": 10}
        ),
        html.Div([
            html.Div([
                html.H5(children="y axis (scatter)"),
            ], style={"padding-top": 8}),
            dcc.Dropdown(id="y_axis", clearable=False), ],
            style={"width": "45%", "display": "inline-block", "margin": 10}
        ),
        dcc.Graph(id="scatter-plot"),
    ], style={"width": "30%", "display": "inline-block", "float": "left"}),
    html.Div([
        html.Div([
            html.Div([
                html.H5(children="x axis (histogram)"),
            ], style={"padding-top": 8}),
            dcc.Dropdown(id="x_axis_histo", clearable=False)
        ], style={"margin": 10}),
        dcc.Graph(id="histogram"),
    ], style={"width": "30%", "display": "inline-block", "float": "left"}),
    html.Div([
        html.Div([
            html.Div([
                html.H5(children="Choose a data file"),
            ], style={"margin-top": 8}),
            html.Div([
                dcc.Dropdown(data_files, id="data_files", clearable=False),
            ], style={"width": "95%", }),
            html.Button("Load the data file", id="submit-button",
                        n_clicks=0, className="btn btn-primary"),
            html.H3(id="chosen_data_file"),
        ], style={"padding-left": 10}),
        html.Div([
            html.P(id="selected"),
        ], style={"display": "flex", "padding-left": "10px", "padding-top": "4px"}),
    ], style={
        "width": "30%", "display": "inline-block",
        "margin": 10, "float": "left", "background-color": "#dffcde",
        "height": "800px", "border-radius": "8px"})
])


@app.callback(
    Output("chosen_data_file", "children"),
    Output("x_axis", "options"),
    Output("y_axis", "options"),
    Output("x_axis_histo", "options"),
    Input("submit-button", "n_clicks"),
    State("data_files", "value"),
    prevent_initial_call=True,
)
def choose_data_file(n_clicks, filename):
    """
        User chooses a data file to load. Column names are sent to show a histogram and a scatter. 

        Returns:
            File name as a string and all the columns' names
    """
    df = read_data_file(filename)
    columns = df.columns.tolist()
    return f"Data file: {filename}", columns, columns, columns


@app.callback(
    Output("scatter-plot", "figure"),
    Input("x_axis", "value"), Input("y_axis", "value"),
    State("data_files", "value"),
    prevent_initial_call=True
)
def render_scatter(x_axis, y_axis, filename):
    """
        Returns a plotly's scatter object with axes given by the user.

        Returns:
            Scatter object
    """
    df = read_data_file(filename)
    fig = px.scatter(df, x=x_axis, y=y_axis)
    return fig


@app.callback(
    Output("histogram", "figure"),
    Input("x_axis_histo", "value"),
    State("data_files", "value"),
    prevent_initial_call=True,
)
def render_histogram(x_axis, filename):
    """
        Returns a plotly's histogram object with a x axis given by the user

        Returns:
            Histogram object
    """
    df = read_data_file(filename)
    fig = px.histogram(df, x=x_axis)
    return fig


@app.callback(
    Output("selected", "children"),
    Input("scatter-plot", "selectedData"),
    prevent_initial_call=True
)
def selected_data(data):
    points = [point["pointIndex"] for point in data["points"]]
    return str(points)


def start():
    # if __name__ == "__main__":
    app.run_server()
