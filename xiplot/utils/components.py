from typing import Any, Dict, Optional
import base64
from io import BytesIO

import plotly as po
from dash import dcc, html, Dash, Input, Output, State, ALL, ctx, no_update, MATCH
from dash_extensions.enrich import State

from xiplot.utils import generate_id


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


class DeleteButton(html.Button):
    def __init__(self, index: Any, children: str = "x", **kwargs: Any):
        """Create a delete button.

        Args:
            index: Which index should be deleted.
            children: The visuals of the button. Defaults to "x".
            **kwargs: additional arguments forwarded to `html.Button`.
        """
        super().__init__(
            children=children,
            id=generate_id(DeleteButton, index),
            className="delete",
            **kwargs
        )


class PdfButton(html.Button):
    def __init__(self, index: Any, children: str = "Download as pdf", **kwargs: Any):
        """Create a button for donwloading plots as pdf.

        Args:
            index: Which plot should be downloaded.
            children: The text of the button. Defaults to "Download as pdf".
            **kwargs: additional arguments forwarded to `html.Button`.
        """
        super().__init__(children=children, id=generate_id(type(self), index), **kwargs)

    @classmethod
    def create_global(cls) -> Any:
        """Create the `dcc.Download` component needed for the pdf button (add it to your layout)."""
        return dcc.Download(id=generate_id(cls, None, "download"))

    @classmethod
    def register_callback(cls, app: Dash, graph_id: Dict[str, Any]):
        """Register callbacks.
        NOTE: Currently this method has to be called separately for every type of graph.
        This is because Dash cannot match based on properties (i.e., select only the `State`s with a "figure" property).

        Args:
            app: Xiplot app.
            graph_id: Id of the graph.
        """
        graph_id["index"] = ALL

        @app.callback(
            Output(generate_id(cls, None, "download"), "data"),
            Input(generate_id(cls, ALL), "n_clicks"),
            State(graph_id, "figure"),
            prevent_initial_call=True,
        )
        def download_as_pdf(n_clicks, fig):
            if ctx.triggered[0]["value"] is None:
                return no_update

            figs = ctx.args_grouping[1]

            figure = None
            for f in figs:
                if f["id"]["index"] == ctx.triggered_id["index"]:
                    figure = f["value"]
            if not figure:
                return no_update
            fig_img = po.io.to_image(figure, format="pdf")
            file = BytesIO(fig_img)
            encoded = base64.b64encode(file.getvalue()).decode("ascii")
            return dict(
                base64=True,
                content=encoded,
                filename="xiplot.pdf",
                type="application/pdf",
            )
