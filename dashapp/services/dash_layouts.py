from dash import html, dcc
import plotly.express as px

from dashapp.services.data_frame import get_data_files


TABS = [
    dcc.Tab(label="Data", value="control-data-tab"),
    dcc.Tab(label="Plots", value="control-plots-tab"),
    dcc.Tab(label="Clusters", value="control-clusters-tab"),
]


def app_logo():
    layout = html.Div(
        [html.H1("Dash App 2022")], style={"text-align": "center", "margin": 20}
    )
    return layout


def control(plot_types):
    layout = html.Div(
        [
            app_logo(),
            dcc.Tabs(id="control-tabs", value="control-data-tab", children=TABS),
            control_data_content(),
            control_plots_content(plot_types),
            control_clusters_content(),
        ],
        style={
            "width": "100%",
            "display": "inline-block",
            "background-color": "#dffcde",
            "height": "auto",
            "border-radius": "8px",
        },
    )

    return layout


def control_data_content():
    try:
        import dash_uploader as du

        uploader = du.Upload(
            id="file_uploader", text="Drag and Drop or Select a File to upload"
        )
    except ImportError:
        uploader = dcc.Upload(
            id="file_uploader",
            children=html.Div(
                [
                    "Drag and Drop or ",
                    html.A("Select a File"),
                    " to upload",
                ]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
        )

    layout = html.Div(
        [
            layout_wrapper(
                component=dcc.Dropdown(
                    get_data_files(), id="data_files", clearable=False
                ),
                title="Choose a data file",
                style={"width": "98%"},
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
            html.Div([uploader], style={"padding-top": "2%"}),
        ],
        id="control_data_content-container",
        style={"display": "none"},
    )

    return layout


def control_plots_content(plot_types):
    layout = html.Div(
        [
            layout_wrapper(
                component=dcc.Dropdown(
                    options=[plot_type for plot_type in plot_types], id="plot_type"
                ),
                title="Select a plot type",
                style={"width": "98%"},
            ),
            html.Button("Add", id="new_plot-button"),
        ],
        id="control_plots_content-container",
        style={"display": "none"},
    )

    return layout


def control_clusters_content():
    layout = html.Div(
        [
            layout_wrapper(
                component=dcc.Dropdown(
                    options=[i for i in range(2, 11)], id="cluster_amount"
                ),
                title="cluster amount",
                style={"width": "23%", "display": "inline-block", "padding-left": "2%"},
            ),
            layout_wrapper(
                component=dcc.Dropdown(id="cluster_feature", multi=True),
                title="features",
                style={"width": "50%", "display": "inline-block", "padding-left": "2%"},
            ),
            html.Div(
                [html.Button("Run", id="cluster-button")],
                style={"padding-left": "2%", "padding-top": "2%"},
            ),
            html.Div(
                [html.H4(id="clusters_created_message")],
                id="clusters_created_message-container",
                style={"display": "none"},
            ),
            layout_wrapper(
                component=dcc.Dropdown(
                    id="selection_cluster_dropdown",
                    clearable=False,
                    options=[
                        {
                            "label": html.Div(
                                [
                                    html.Div(
                                        style={
                                            "width": 20,
                                            "height": 20,
                                            "display": "inline-block",
                                            "background-color": px.colors.qualitative.Plotly[
                                                0
                                            ],
                                        }
                                    ),
                                    html.Div(
                                        "background",
                                        style={
                                            "display": "inline-block",
                                            "padding-left": 10,
                                        },
                                    ),
                                ]
                            ),
                            "value": "bg",
                        }
                    ]
                    + [
                        {
                            "label": html.Div(
                                [
                                    html.Div(
                                        style={
                                            "width": 20,
                                            "height": 20,
                                            "display": "inline-block",
                                            "background-color": c,
                                        }
                                    ),
                                    html.Div(
                                        f"cluster #{i+1}",
                                        style={
                                            "display": "inline-block",
                                            "padding-left": 10,
                                        },
                                    ),
                                ]
                            ),
                            "value": f"c{i+1}",
                        }
                        for i, c in enumerate(px.colors.qualitative.Plotly[1:])
                    ],
                ),
                title="Selection Cluster:",
            ),
            layout_wrapper(
                component=dcc.Dropdown(
                    id="comparison_cluster_dropdown",
                    clearable=False,
                    options=[
                        {
                            "label": html.Div(
                                [
                                    html.Div(
                                        style={
                                            "width": 20,
                                            "height": 20,
                                            "display": "inline-block",
                                            "background-color": px.colors.qualitative.Plotly[
                                                0
                                            ],
                                        }
                                    ),
                                    html.Div(
                                        "background",
                                        style={
                                            "display": "inline-block",
                                            "padding-left": 10,
                                        },
                                    ),
                                ]
                            ),
                            "value": "bg",
                        }
                    ]
                    + [
                        {
                            "label": html.Div(
                                [
                                    html.Div(
                                        style={
                                            "width": 20,
                                            "height": 20,
                                            "display": "inline-block",
                                            "background-color": c,
                                        }
                                    ),
                                    html.Div(
                                        f"cluster #{i+1}",
                                        style={
                                            "display": "inline-block",
                                            "padding-left": 10,
                                        },
                                    ),
                                ]
                            ),
                            "value": f"c{i+1}",
                        }
                        for i, c in enumerate(px.colors.qualitative.Plotly[1:])
                    ],
                ),
                title="Comparison Cluster:",
            ),
        ],
        id="control_clusters_content-container",
        style={"display": "none"},
    )

    return layout


def smiles():
    layout = html.Div([html.Div(id="smiles_image")], style={"float": "left"})

    return layout


def layout_wrapper(component, id="", style=None, css_class=None, title=None):
    layout = html.Div(
        children=[html.Div(title), component],
        id=id,
        style=style
        if style
        else {
            "width": "40%",
            "display": "inline-block",
            "padding-left": "2%",
        },
        className=css_class,
    )

    return layout
