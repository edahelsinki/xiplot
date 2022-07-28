from dash import html, dcc

from dashapp.utils.cluster import cluster_colours


def layout_wrapper(component, id="", style=None, css_class=None, title=None):
    layout = html.Div(
        children=[html.Div(title), component],
        id=id,
        style=style,
        className=css_class,
    )

    return layout


def delete_button(type, index):
    return html.Button(
        "x", id={"type": type, "index": index}, style={"background-color": "red"}
    )


def cluster_dropdown(
    id,
    index=None,
    multi=False,
    clearable=False,
    value=None,
    style=None,
    title=None,
    css_class=None,
):
    layout = layout_wrapper(
        component=dcc.Dropdown(
            id={"type": id, "index": index} if index else id,
            clearable=clearable,
            multi=multi,
            searchable=False,
            value=value,
            options=[
                {
                    "label": html.Div(
                        [
                            html.Div(
                                style={"background-color": colour},
                                className="color-rect",
                            ),
                            html.Div(
                                "everything" if cluster == "all" else f"cluster #{i}",
                                style={
                                    "display": "inline-block",
                                    "padding-left": 10,
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "align-items": "center",
                        },
                    ),
                    "value": cluster,
                }
                for i, (cluster, colour) in enumerate(cluster_colours().items())
            ],
        ),
        title=title,
        css_class=css_class,
        style=style,
    )
    return layout
