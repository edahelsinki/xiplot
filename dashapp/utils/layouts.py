from dash import html


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
