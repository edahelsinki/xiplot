from dash import no_update
from dashapp.utils.dataframe import get_smiles_column_name


def get_smiles_inputs(smiles_render_modes, render_mode, smiles_inputs, df, row):
    """
    Sets given SMILES string to specific SMILES inputs based on render mode

    Parameters:

        smiles_render_modes: list of render modes of SMILES components
        render_mode: render mode that is wanted to be modified
        smiles_inputs: current values of SMILES inputs
        df: pandas.DataFrame
        row: row id of the SMILES string that will be set

    Returns:
        smiles_inputs: list of SMILES inputs' values
    """
    for id, input in enumerate(smiles_inputs):
        if input is None:
            smiles_inputs[id] = ""

    if render_mode not in smiles_render_modes:
        return no_update

    ids = []
    for id, mode in enumerate(smiles_render_modes):
        if mode != render_mode:
            continue
        ids.append(id)

    smiles_col = get_smiles_column_name(df)
    for i in ids:
        smiles_inputs[i] = df.iloc[row][smiles_col]

    return smiles_inputs
