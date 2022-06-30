from dash import html, dcc
from services.data_frame import get_data_files


TABS = [
    dcc.Tab(label="Data", value="control-data-tab"),
    dcc.Tab(label="Scatter plot", value="control-scatterplot-tab"),
    dcc.Tab(label="Clusters", value="control-clusters-tab"),
]


def app_logo():
    layout = html.Div(
        [html.H1("Dash App 2022")], style={"text-align": "center", "margin": 20}
    )
    return layout


def control():
    layout = html.Div(
        [
            app_logo(),
            dcc.Tabs(id="control-tabs", value="control-data-tab", children=TABS),
            control_data_content(),
            control_scatterplot_content(),
            control_clusters_content(),
        ],
        style={
            "width": "32%",
            "display": "inline-block",
            "float": "right",
            "background-color": "#dffcde",
            "height": "600px",
            "border-radius": "8px",
        },
    )

    return layout


def control_data_content():
    layout = html.Div(
        [
            html.Div(
                [
                    html.H4(children="Choose a data file"),
                ],
                style={"margin-top": 4},
            ),
            html.Div(
                [
                    dcc.Dropdown(get_data_files(), id="data_files", clearable=False),
                ],
                style={
                    "width": "98%",
                },
            ),
            html.Div(
                [
                    html.Button(
                        "Load the data file",
                        id="submit-button",
                        n_clicks=0,
                        className="btn btn-primary",
                    ),
                ],
                style={
                    "padding-top": "2%",
                },
            ),
            html.Div(
                [html.H4(id="data_file_load_message")],
                id="data_file_load_message-container",
                style={"display": "none"},
            ),
        ],
        id="control_data_content-container",
        style={"display": "none"},
    )

    return layout


def control_scatterplot_content():
    layout = html.Div(
        [
            html.Div(
                [
                    html.H4("Scatterplot"),
                ]
            ),
            html.Div(
                [
                    dcc.RadioItems(
                        id="algorythm",
                        options=["PCA", "Slisemap"],
                    )
                ]
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    "target (color)",
                                ],
                            ),
                            dcc.Dropdown(
                                id="scatter_target_color",
                            ),
                        ],
                        style={
                            "width": "40%",
                            "display": "inline-block",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    "target (symbol)",
                                ]
                            ),
                            dcc.Dropdown(
                                id="scatter_target_symbol",
                            ),
                        ],
                        style={
                            "width": "40%",
                            "display": "inline-block",
                            "padding-left": "2%",
                        },
                    ),
                    html.Div(
                        [
                            html.Div([html.H5("jitter (float)")]),
                            dcc.Slider(
                                id="jitter-slider",
                                min=0,
                                max=1,
                                marks=None,
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                        ]
                    ),
                ],
                style={"padding-top": "2%"},
            ),
        ],
        id="control_scatter_content-container",
        style={"display": "none"},
    )
    return layout


def control_clusters_content():
    layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H5("amount of clusters"),
                        ]
                    ),
                    dcc.Dropdown(
                        options=[i for i in range(2, 11)], id="cluster_amount"
                    ),
                ],
                style={"width": "23%", "display": "inline-block", "padding-left": "2%"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H5("features"),
                        ]
                    ),
                    dcc.Dropdown(id="cluster_feature", multi=True),
                ],
                style={"width": "50%", "display": "inline-block", "padding-left": "2%"},
            ),
            html.Div(
                [html.Button("Run", id="cluster_button")],
                style={"padding-left": "2%", "padding-top": "2%"},
            ),
        ],
        id="control_clusters_content-container",
        style={"display": "none"},
    )

    return layout


def scatterplot():
    layout = html.Div(
        id="scatterplot-container",
        children=[dcc.Graph(id="scatterplot")],
        style={"display": "none"},
    )

    return layout


def histogram():
    layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H5(children="x axis (histogram)"),
                        ],
                        style={"padding-top": 8},
                    ),
                    dcc.Dropdown(id="x_axis_histo", clearable=False),
                ],
                style={"margin-top": 10, "margin-left": "10%", "width": "82%"},
            ),
            dcc.Graph(id="histogram"),
            html.Div(
                [html.P(id="histo_mean"), html.P(id="histo_deviation")],
                style={"textAlign": "center"},
            ),
        ],
        id="histogram-container",
        style={"display": "none"},
    )

    return layout


def smiles():
    layout = html.Div([html.Div(id="smiles_image")], style={"float": "left"})

    return layout
