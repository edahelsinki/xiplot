from dash import html, dcc
import plotly.express as px


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


def delete_button(type, index):
    return html.Button(
        "x", id={"type": type, "index": index}, style={"background-color": "red"}
    )


def cluster_dropdown(id, index, selection: bool):
    layout = layout_wrapper(
        component=dcc.Dropdown(
            id={"type": id, "index": index},
            clearable=False,
            value="c1" if selection else "all",
            options=[
                {
                    "label": html.Div(
                        [
                            html.Div(
                                style={
                                    "width": 20,
                                    "height": 20,
                                    "display": "inline-block",
                                    "background-color": px.colors.qualitative.Plotly[0],
                                }
                            ),
                            html.Div(
                                "everything",
                                style={
                                    "display": "inline-block",
                                    "padding-left": 10,
                                },
                            ),
                        ]
                    ),
                    "value": "all",
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
        title="Selection Cluster" if selection else "Comparison Cluster",
        style={"margin-left": "10%", "display": "inline-block", "width": "40%"}
        if selection
        else None,
    )
    return layout
