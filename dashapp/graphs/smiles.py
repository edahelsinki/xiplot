from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import delete_button, layout_wrapper
from dashapp.utils.dataframe import get_smiles_column_name
from dashapp.graphs import Graph


class Smiles(Graph):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        app.clientside_callback(
            """
            async function svgFromSMILES(smiles) {
                if (!window.RDKit) {
                    window.RDKit = await window.initRDKitModule();
                }

                const mol = window.RDKit.get_mol(smiles);
                const svg = mol
                    .get_svg()
                    .replace(/<rect[^>]*>\s*<\/rect>/, "")
                    .split(/\s+/)
                    .join(" ");

                return "data:image/svg+xml;base64," + btoa(svg);
            }
            """,
            Output({"type": "smiles-display", "index": MATCH}, "src"),
            Input({"type": "smiles-input", "index": MATCH}, "value"),
        )

        @app.callback(
            output=dict(
                smiles=Output({"type": "smiles-input", "index": ALL}, "value"),
                scatter=Output({"type": "scatterplot", "index": ALL}, "hoverData"),
            ),
            inputs=[
                Input({"type": "scatterplot", "index": ALL}, "hoverData"),
                Input("data_frame_store", "data"),
            ],
        )
        def render_hovered_smiles(hover, df):
            if ctx.triggered_id == "data_frame_store":
                raise PreventUpdate()

            df = df_from_store(df)

            row = None
            for h in hover:
                if h:
                    row = h["points"][0]["customdata"][0]["index"]
            if not row:
                raise PreventUpdate()

            smiles_col = get_smiles_column_name(df)

            if not smiles_col:
                raise PreventUpdate()
            smiles_amount = len(ctx.outputs_grouping["smiles"])
            scatter_amount = len(ctx.outputs_grouping["scatter"])
            return dict(
                smiles=[df.iloc[row][smiles_col] for _ in range(smiles_amount)],
                scatter=[None] * scatter_amount,
            )

        @app.callback(
            output=dict(
                smiles=Output({"type": "smiles-input", "index": ALL}, "value"),
            ),
            inputs=[
                Input({"type": "table", "index": ALL}, "active_cell"),
                State("data_frame_store", "data"),
            ],
        )
        def render_active_cell_smiles(active_cell, df):
            df = df_from_store(df)
            smiles_col = get_smiles_column_name(df)

            if not smiles_col:
                raise PreventUpdate()

            row, column = None, None
            for cell in active_cell:
                if cell:
                    row = cell["row"]
                    column = cell["column_id"]

            if not row or not column or column != smiles_col:
                raise PreventUpdate()
            smiles_amount = len(ctx.outputs_grouping["smiles"])
            return dict(
                smiles=[df.iloc[row][smiles_col] for _ in range(smiles_amount)],
            )

    @staticmethod
    def create_new_layout(index, df, columns):
        return html.Div(
            children=[
                delete_button("plot-delete", index),
                html.Br(),
                html.Img(id={"type": "smiles-display", "index": index}, width="100%"),
                html.Br(),
                layout_wrapper(
                    dcc.Input(
                        id={"type": "smiles-input", "index": index},
                        type="text",
                        debounce=True,
                        placeholder="SMILES string",
                    ),
                    title="SMILES string",
                ),
            ],
            id={"type": "smiles-container", "index": index},
            className="graphs",
        )
