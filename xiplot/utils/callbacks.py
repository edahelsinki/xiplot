import base64
import dash
import plotly as po
from io import BytesIO

from dash import Input, Output, ALL, ctx


def pdf_callback(app, type):
    @app.callback(
        Output("graph_to_pdf", "data"),
        Input({"type": "download_pdf_btn", "index": ALL}, "n_clicks"),
        Input({"type": type, "index": ALL}, "figure"),
        prevent_initial_call=True,
    )
    def download_as_pdf(n_clicks, fig):
        if (
            ctx.triggered[0]["value"] is None
            or ctx.triggered_id["type"] != "download_pdf_btn"
        ):
            return dash.no_update

        figs = ctx.args_grouping[1]

        figure = None
        for f in figs:
            if f["id"]["index"] == ctx.triggered_id["index"]:
                figure = f["value"]
        if not figure:
            return dash.no_update
        fig_img = po.io.to_image(figure, format="pdf")
        file = BytesIO(fig_img)
        encoded = base64.b64encode(file.getvalue()).decode("ascii")
        return dict(
            base64=True,
            content=encoded,
            filename="xiplot.pdf",
            type="application/pdf",
        )
