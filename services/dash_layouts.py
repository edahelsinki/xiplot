from dash import html, dcc
from services.data_frame import get_data_files


def app_logo():
    layout = html.Div([
        html.H1("Dash App 2022")
    ], style={"text-align": "center", "margin": 20})
    return layout


def control():
    layout = html.Div([
        html.Div([
            html.Div([
                html.H5(children="Choose a data file"),
            ], style={"margin-top": 8}),
            html.Div([
                dcc.Dropdown(get_data_files(),
                             id="data_files", clearable=False),
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
        "height": "600px", "border-radius": "8px"})

    return layout


def scatterplot():
    layout = html.Div([
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
    ], style={"width": "33%", "display": "inline-block", "float": "left"})

    return layout


def histogram():
    layout = html.Div([
        html.Div([
            html.Div([
                html.H5(children="x axis (histogram)"),
            ], style={"padding-top": 8}),
            dcc.Dropdown(id="x_axis_histo", clearable=False)
        ], style={"margin-top": 10, "margin-left": "10%", "width": "82%"}),
        dcc.Graph(id="histogram"),
        html.Div([html.P(id="histo_mean"), html.P(
            id="histo_deviation")], style={"textAlign": "center"})
    ], style={"width": "33%", "display": "inline-block", "float": "left"})

    return layout


def selected_histogram():
    layout = html.Div([
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
            dcc.Graph(id="selected_histogram"),
            html.Div([html.P(id="selected_mean"), html.P(
                id="selected_deviation")], style={"textAlign": "center"})
        ])
    ], style={"width": "33%", "display": "inline-block", "float": "left"})

    return layout


def smiles():
    layout = html.Div([
        html.Div(id="smiles_image")
    ], style={"float": "left"})

    return layout
