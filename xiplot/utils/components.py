from typing import Optional
from dash import dcc, html


class FlexRow(html.Div):
    def __init__(self, *components, className: Optional[str] = None, **kwargs):
        if className is None:
            className = "flex-row"
        else:
            className = className + " flex-row"
        super().__init__(children=list(components), className=className, **kwargs)
