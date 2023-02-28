import pandas as pd
import dash
import jsonschema

from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate
from xiplot.utils.components import DeleteButton

from xiplot.utils.layouts import layout_wrapper
from xiplot.utils.dataframe import get_smiles_column_name
from xiplot.utils.smiles import get_smiles_inputs
from xiplot.plots import APlot


class Smiles(APlot):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        app.clientside_callback(
            """
            async function svgFromSMILES(smiles) {
                if (!window.RDKit) {
                    window.RDKit = await window.initRDKitModule();
                }
                const INVALID_SVG = `<?xml version='1.0' encoding='iso-8859-1'?>
                    <svg version='1.1' baseProfile='full'
                      xmlns='http://www.w3.org/2000/svg'
                      xmlns:rdkit='http://www.rdkit.org/xml'
                      xmlns:xlink='http://www.w3.org/1999/xlink'
                      xml:space='preserve'
                      width='250px' height='200px' viewBox='0 0 250 200'
                    >
                        <line x2='200' y2='175' x1='50' y1='25' stroke='#c0392b' stroke-width='5' />
                        <line x2='50' y2='175' x1='200' y1='25' stroke='#c0392b' stroke-width='5' />
                    </svg>
                `;
                const mol = window.RDKit.get_mol(smiles);
                const svg = smiles && mol
                    .get_svg()
                    .replace(/<rect[^>]*>\\s*<\\/rect>/, "")
                    .split(/\\s+/)
                    .join(" ");

                return "data:image/svg+xml;base64," + btoa(svg || INVALID_SVG);
            }
            """,
            Output({"type": "smiles-display", "index": MATCH}, "src"),
            Input({"type": "smiles-input", "index": MATCH}, "value"),
            prevent_initial_call=False,
        )

        @app.callback(
            output=dict(smiles=Output({"type": "smiles-input", "index": ALL}, "value")),
            inputs=[
                Input("lastly_clicked_point_store", "data"),
                State({"type": "smiles_lock_dropdown", "index": ALL}, "value"),
                State({"type": "smiles-input", "index": ALL}, "value"),
                State("data_frame_store", "data"),
            ],
        )
        def render_clicks(row, render_modes, smiles_inputs, df):
            df = df_from_store(df)
            smiles_col = get_smiles_column_name(df)

            if not smiles_col or render_modes == [None]:
                raise PreventUpdate()

            smiles_inputs = get_smiles_inputs(
                render_modes, "click", smiles_inputs, df, row
            )
            return dict(smiles=smiles_inputs)

        @app.callback(
            output=dict(smiles=Output({"type": "smiles-input", "index": ALL}, "value")),
            inputs=[
                Input("lastly_hovered_point_store", "data"),
                State({"type": "smiles_lock_dropdown", "index": ALL}, "value"),
                State({"type": "smiles-input", "index": ALL}, "value"),
                State("data_frame_store", "data"),
            ],
        )
        def render_hovered(row, render_modes, smiles_inputs, df):
            df = df_from_store(df)
            smiles_col = get_smiles_column_name(df)

            if not smiles_col or render_modes == [None]:
                raise PreventUpdate()

            smiles_inputs = get_smiles_inputs(
                render_modes, "hover", smiles_inputs, df, row
            )
            return dict(smiles=smiles_inputs)

        @app.callback(
            output=dict(
                meta=Output("metadata_store", "data"),
            ),
            inputs=[
                State("metadata_store", "data"),
                Input({"type": "smiles_lock_dropdown", "index": ALL}, "value"),
                Input({"type": "smiles-input", "index": ALL}, "value"),
            ],
            prevent_initial_call=False,
        )
        def update_settings(meta, render_modes, smiles_inputs):
            if meta is None:
                return dash.no_update

            for render_mode, smiles_input in zip(*ctx.args_grouping[1 : 2 + 1]):
                if not render_mode["triggered"] and not smiles_input["triggered"]:
                    continue

                index = render_mode["id"]["index"]
                render_mode = render_mode["value"]
                smiles_input = smiles_input["value"]

                meta["plots"][index] = dict(
                    type=Smiles.name(),
                    mode=render_mode,
                    smiles=smiles_input,
                )

            return dict(meta=meta)

        return [
            render_clicks,
            render_hovered,
            update_settings,
        ]

    @staticmethod
    def create_new_layout(index, df, columns, config=dict()):
        jsonschema.validate(
            instance=config,
            schema=dict(
                type="object",
                properties=dict(
                    mode=dict(enum=["hover", "click", "lock"]),
                    smiles=dict(type="string"),
                ),
            ),
        )

        render_mode = config.get("mode", "hover")
        smiles_input = config.get("smiles", "O.O[Fe]=O")

        return html.Div(
            children=[
                DeleteButton(index),
                html.Br(),
                html.Img(
                    id={"type": "smiles-display", "index": index},
                    className="smiles-img",
                ),
                html.Br(),
                layout_wrapper(
                    dcc.Input(
                        id={"type": "smiles-input", "index": index},
                        type="text",
                        value=smiles_input,
                        debounce=True,
                        placeholder="SMILES string",
                    ),
                    css_class="dcc-input",
                    title="SMILES string",
                ),
                layout_wrapper(
                    dcc.Dropdown(
                        id={"type": "smiles_lock_dropdown", "index": index},
                        value=render_mode,
                        options=["hover", "click", "lock"],
                        clearable=False,
                        searchable=False,
                    ),
                    css_class="dd-smiles",
                ),
            ],
            id={"type": "smiles-container", "index": index},
            className="plots",
        )
