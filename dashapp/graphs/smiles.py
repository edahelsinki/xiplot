from dash import html, dcc, Output, Input, State, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import delete_button, layout_wrapper
from dashapp.utils.dataframe import get_smiles_column_name
from dashapp.utils.smiles import get_smiles_inputs
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
                    column = cell["column_id"]
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
            ),
            inputs=[
                Input("lastly_clicked_point_store", "data"),
                State({"type": "smiles_lock_dropdown", "index": ALL}, "value"),
                State({"type": "smiles-input", "index": ALL}, "value"),
                State("data_frame_store", "data"),
                State({"type": "table", "index": ALL}, "selected_rows"),
            ],
        )
        def render_active_cell_smiles(
            row, smiles_render_modes, smiles_inputs, df, selected_rows
        ):
            # FIXME wrong smiles img is shown if some rows are selected
            df = df_from_store(df)
            smiles_col = get_smiles_column_name(df)

            if not smiles_col or smiles_col != smiles_col:
                raise PreventUpdate()

            smiles_amount = len(smiles_inputs)
            smiles = []
            for i in range(smiles_amount):
                if smiles_render_modes[i] == "lock":
                    smiles.append(smiles_inputs[i])
                else:
                    smiles.append(df.iloc[row][smiles_col])

            return dict(smiles=smiles)

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
            if render_modes == [None]:
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
            if render_modes == [None]:
                raise PreventUpdate()

            smiles_inputs = get_smiles_inputs(
                render_modes, "hover", smiles_inputs, df, row
            )
            return dict(smiles=smiles_inputs)

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
                    css_class="dcc-input",
                    title="SMILES string",
                ),
                layout_wrapper(
                    dcc.Dropdown(
                        id={"type": "smiles_lock_dropdown", "index": index},
                        value="hover",
                        options=["hover", "click", "lock"],
                        clearable=False,
                        searchable=False,
                    ),
                    css_class="dd-double-right",
                ),
            ],
            id={"type": "smiles-container", "index": index},
            className="graphs",
        )
