from dash import html


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
