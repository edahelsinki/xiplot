from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import delete_button, layout_wrapper
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
            output=dict(smiles=Output({"type": "smiles-input", "index": ALL}, "value")),
            inputs=[
                Input({"type": "scatterplot", "index": ALL}, "hoverData"),
                State("data_frame_store", "data"),
            ],
        )
        def render_hovered_smiles(hover, df):
            df = df_from_store(df)
            for h in hover:
                if h:
                    row = h["points"][0]["customdata"][0]["index"]
            smiles_amount = len(ctx.outputs_grouping["smiles"])

            smiles_col = None
            for s in ["SMILES", "smiles", "Smiles"]:
                if s in df.columns:
                    smiles_col = s

            if not smiles_col:
                raise PreventUpdate()
            return dict(smiles=[df.iloc[row][smiles_col] for _ in range(smiles_amount)])

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
