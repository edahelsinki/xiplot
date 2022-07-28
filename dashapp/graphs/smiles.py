from dash import html, dcc, Output, Input, MATCH

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
