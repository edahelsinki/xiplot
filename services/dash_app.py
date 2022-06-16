from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import os
from services.data_frame import load_auto_mpg, read_data_file
#from data_frame import load_auto_mpg, read_data_file
from ui.dash_renderer import render_smiles


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
            style={"width": "40%", "display": "inline-block",
                   "margin-left": "10%"}
        ),
        html.Div([
            html.Div([
                html.H5(children="y axis (scatter)"),
            ], style={"padding-top": 8}),
            dcc.Dropdown(id="y_axis", clearable=False), ],
            style={"width": "40%", "display": "inline-block", "margin": 10}
        ),
        dcc.Graph(id="scatter-plot"),
    ], style={"width": "33%", "display": "inline-block", "float": "left"}),
    html.Div([
        html.Div([
            html.Div([
                html.H5(children="x axis (histogram)"),
            ], style={"padding-top": 8}),
            dcc.Dropdown(id="x_axis_histo", clearable=False)
        ], style={"margin-top": 10, "margin-left": "10%", "width": "82%"}),
        dcc.Graph(id="histogram"),
    ], style={"width": "33%", "display": "inline-block", "float": "left"}),
    html.Div([
        html.Div([
            html.Div([
                html.H5(children="Choose a data file"),
            ], style={"margin-top": 8}),
            html.Div([
                dcc.Dropdown(data_files, id="data_files", clearable=False),
            ], style={"width": "98%", }),
            html.Div([
                html.Button("Load the data file", id="submit-button",
                            n_clicks=0, className="btn btn-primary"),
            ], style={"padding-top": "2%", }),
        ], style={"padding-left": "2%"}),
        html.Div([
            html.H5(children="Select data from the scatter plot"),
            html.Div([
                html.P("Selected 0 points", id="selected"),
            ],),
            html.Div([
                html.Div([
                    html.H6("Operation")
                ]),
                html.Div([
                    dcc.Dropdown(id="selected_data_operation")
                ], style={"width": "98%"}),
            ], style={"width": "49%", "display": "inline-block"}),
            html.Div([
                html.Div([
                    html.H6("Column")
                ]),
                html.Div([
                    dcc.Dropdown(id="selected_data_column", clearable=False)
                ], style={"width": "98%"})
            ], style={"width": "49%", "display": "inline-block", "margin": "1%"})
        ], style={"padding-top": "4%", "padding-left": "2%"}),
    ], style={
        "width": "32%", "display": "inline-block",
        "margin": 10, "float": "left", "background-color": "#dffcde",
        "height": "600px", "border-radius": "8px"}),
    html.Div([
        html.Div([
            html.Div([
                html.H5(children="x axis (histogram by selected points)")
            ]),
            html.Div([
                dcc.Dropdown(id="selected_histogram_column", clearable=False)
            ])
        ], style={"width": "40%", "display": "inline-block",
                  "margin-left": "10%"}),
        html.Div([
            dcc.Graph(id="selected_histogram")
        ])
    ], style={"width": "33%", "display": "inline-block", "float": "left"}),
    html.Div([
        html.Div(id="smiles_image")
    ], style={"float": "left"})
])


@app.callback(
    Output("x_axis", "options"),
    Output("y_axis", "options"),
    Output("x_axis_histo", "options"),
    Output("selected_data_column", "options"),
    Output("selected_histogram_column", "options"),
    Output("x_axis", "value"),
    Output("y_axis", "value"),
    Output("x_axis_histo", "value"),
    Output("selected_data_column", "value"),
    Output("selected_histogram_column", "value"),
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
    return columns, columns, columns, columns, columns, columns[0], columns[1], columns[0], columns[0], columns[0]


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
    return f"Selected {len(points)} points"


@app.callback(
    Output("selected_histogram", "figure"),
    Input("scatter-plot", "selectedData"),
    Input("selected_histogram_column", "value"),
    State("data_files", "value"),
    prevent_initial_call=True
)
def render_histogram_by_selected_points(data, x_axis, filename):
    df = read_data_file(filename)
    points = [point["pointIndex"] for point in data["points"]]
    selected_df = df.loc[df.index.isin(points)]
    fig = px.histogram(selected_df, x_axis)
    return fig


@app.callback(
    Output("smiles_image", "children"),
    Input("scatter-plot", "hoverData"),
    State("data_files", "value"),
    prevent_initial_call=True
)
def render_mol_image(hover_data, filename):
    df = read_data_file(filename)
    point = hover_data["points"][0]["pointIndex"]
    smiles_str = df.loc[point]["SMILES"]
    im = render_smiles(smiles_str)

    children = [
        html.Img(
            src=im,
        ),
        html.P(smiles_str)
    ]
    return children


def start():
#if __name__ == "__main__":
    app.run_server()
