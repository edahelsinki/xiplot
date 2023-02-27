from typing import Optional
from dash import dcc, html


class FlexRow(html.Div):
    """
    Create a Div with a "display: flex" style.
    This makes the children appear on one line (with wrapping if necessary).
    Any child with a `className="stretch"` will fill all the empty space of the line.
    `dcc.Dropdown` automatically stretch with a minimum length (see `html_components.css`).

    Example:
        row = FlexRow(dcc.Dropown(["A", "B"]), html.Button("Accept"), id="example")
    """

    def __init__(self, *children, className: Optional[str] = None, **kwargs):
        if className is None:
            className = "flex-row"
        else:
            className = className + " flex-row"
        super().__init__(children=list(children), className=className, **kwargs)
