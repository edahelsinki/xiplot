import dash
import pandas as pd
from dash import MATCH, Input, Output, State, dcc, html

from xiplot.plots import APlot
from xiplot.plugin import ID_CLICKED, ID_DATAFRAME, ID_HOVERED
from xiplot.utils.components import FlexRow, InputText, PlotData
from xiplot.utils.layouts import layout_wrapper


class Smiles(APlot):
    @classmethod
    def name(cls):
        return "SMILES (molecules)"

    @classmethod
    def help(cls):
        return (
            "Render a molecule from a SMILES string\n\nOne column of the"
            " dataset must contain a molecule represented as a SMILES string"
            " (Simplified molecular-input line-entry system)."
        )

    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        app.clientside_callback(
            """
async function svgFromSMILES(smiles) {
    if (!window.RDKit) {
        window.RDKit = await window.initRDKitModule();
    }
    const INVALID_SVG = `
<?xml version='1.0' encoding='iso-8859-1'?>
<svg version='1.1' baseProfile='full'
    xmlns='http://www.w3.org/2000/svg'
    xmlns:rdkit='http://www.rdkit.org/xml'
    xmlns:xlink='http://www.w3.org/1999/xlink'
    xml:space='preserve'
    width='250px' height='200px' viewBox='0 0 250 200'
>
    <line x2='200' y2='175' x1='50' y1='25' stroke='#c0392b' stroke-width='5'/>
    <line x2='50' y2='175' x1='200' y1='25' stroke='#c0392b' stroke-width='5'/>
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
            Output(cls.get_id(MATCH, "display"), "src"),
            Input(cls.get_id(MATCH, "string"), "value"),
            prevent_initial_call=False,
        )

        @app.callback(
            Output(cls.get_id(MATCH, "string"), "value"),
            Input(ID_CLICKED, "data"),
            Input(ID_HOVERED, "data"),
            State(cls.get_id(MATCH, "mode"), "value"),
            State(cls.get_id(MATCH, "col"), "value"),
            State(cls.get_id(MATCH, "string"), "value"),
            State(ID_DATAFRAME, "data"),
            prevent_initial_call=True,
        )
        def update_smiles(rowc, rowh, mode, col, old, df):
            if col is None or col == "":
                return dash.no_update
            if mode == "Click":
                row = rowc
            elif mode == "Hover":
                row = rowh
            else:
                raise Exception("Unknown SMILES mode: " + mode)
            if row is None:
                return dash.no_update
            df = df_from_store(df)
            try:
                new = df[col][row]
                if old != new:
                    return new
                return dash.no_update
            except Exception:
                return dash.no_update

        PlotData.register_callback(
            cls.name(),
            app,
            dict(
                mode=Input(cls.get_id(MATCH, "mode"), "value"),
                smiles=Input(cls.get_id(MATCH, "string"), "value"),
                column=Input(cls.get_id(MATCH, "col"), "value"),
            ),
        )

        return update_smiles

    @classmethod
    def create_layout(cls, index, df: pd.DataFrame, columns, config=dict()):
        import jsonschema

        jsonschema.validate(
            instance=config,
            schema=dict(
                type="object",
                properties=dict(
                    mode=dict(enum=["Hover", "Click"]),
                    smiles=dict(type="string"),
                    column=dict(type="string"),
                ),
            ),
        )

        cols = [
            c
            for c in df.select_dtypes([object, "category"])
            if isinstance(df[c][0], str)
        ]
        column = next((c for c in cols if "smiles" in c.lower()), "")

        render_mode = config.get("mode", "Hover")
        smiles_input = config.get("smiles", "")
        column = config.get("column", column)

        return [
            html.Img(
                id=cls.get_id(index, "display"),
                className="smiles-img",
            ),
            html.Br(),
            FlexRow(
                layout_wrapper(
                    dcc.Dropdown(
                        id=cls.get_id(index, "col"), value=column, options=cols
                    ),
                    title="SMILES column",
                    css_class="dash-dropdown",
                ),
                layout_wrapper(
                    dcc.Dropdown(
                        id=cls.get_id(index, "mode"),
                        value=render_mode,
                        options=["Hover", "Click"],
                        clearable=False,
                        searchable=False,
                    ),
                    title="Selection mode",
                    css_class="dash-dropdown",
                ),
                layout_wrapper(
                    InputText(
                        id=cls.get_id(index, "string"),
                        value=smiles_input,
                        debounce=True,
                        placeholder="SMILES string, e.g., 'O.O[Fe]=O'",
                    ),
                    css_class="dash-input",
                    title="SMILES string",
                ),
            ),
        ]
