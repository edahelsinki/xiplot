import time
import pandas as pd
import dash

from dashapp.setup import setup_dash_app
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from tests.util_test import render_plot
from dashapp.plots.table import Table

(
    update_table_data,
    update_selected_rows_store,
    update_table_checkbox,
    update_lastly_activated_cell,
    update_table_columns,
    sync_with_input,
    add_matching_values,
    update_settings,
) = Table.register_callbacks(dash.Dash(__name__), lambda x: x, lambda x: x)


def test_teta001_create_table():
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    output = update_table_data(["all", "all"], [True, True], df, [df], [[]])
    table_df = output[0][0][0]
    sort_by = output[1][0]

    assert table_df == {"col1": 1, "col2": 3, "Selection": True, "Clusters": "all"}, {
        "col1": 2,
        "col2": 4,
        "Selection": True,
        "Clusters": "all",
    }
    assert sort_by == []


def test_update_selected_rows_store():
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    output = update_selected_rows_store([[1]], df)
    selected_rows_store = output

    assert selected_rows_store == [True, False]


def test_update_table_checkbox():
    output = update_table_checkbox([True, False], ["all", "all"])
    selected_rows = output["table"]

    assert selected_rows == [[1]]


def test_update_lastly_activated_cell():
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    output = update_lastly_activated_cell([{"row": 1, "column_id": "col1"}], df)
    lastly_activated_cell_row = output["cell_store"]
    updated_active_cell = output["active_cell"]

    assert lastly_activated_cell_row == 1
    assert updated_active_cell == [None]
