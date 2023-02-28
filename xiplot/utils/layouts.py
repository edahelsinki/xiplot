import uuid

from dash import html, dcc

from xiplot.utils.cluster import cluster_colours


def layout_wrapper(component, id="", style=None, css_class=None, title=None):
    """
    Wraps a dash component to a html.Div element

    Parameters:

        component: dash core component
        id: id of the html.Div element
        style: style of the html.Div element
        css_class: className of the html.Div
        title: title of the dash core component

    Returns:

        layout: html.Div element
    """
    layout = html.Div(
        children=[html.Div(title), component],
        id=id,
        style=style,
        className=css_class,
    )
    return layout


def cluster_dropdown(
    id_name,
    id_index=None,
    multi=False,
    clearable=False,
    value=None,
    style=None,
    title=None,
    css_class=None,
    disabled=False,
):
    """
    Wraps a cluster dropdown to a html.Div element

    Parameter:

        id_name: name of the id
        id_index: index of the id
        multi (boolean): if True, the user can set multiple values
        clearable (boolean): if True, the user can clear all the values of the dropdown
        value: initial value of the dropdown when it's created
        style: style of the html.Div element
        title: title of the dropdown
        css_class: className of the html.Div element

    Returns:

        layout: html.Div element
    """
    layout = layout_wrapper(
        component=dcc.Dropdown(
            id={"type": id_name, "index": id_index} if id_index else id_name,
            clearable=clearable,
            multi=multi,
            searchable=False,
            value=value,
            disabled=disabled,
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
                            html.Div(
                                id={
                                    "type": f"cluster-dropdown-count",
                                    "index": f"{cluster}-{uuid.uuid4()}",
                                },
                                style={
                                    "display": "inline-block",
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
