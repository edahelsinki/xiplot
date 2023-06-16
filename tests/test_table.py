import time

import dash
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.util_test import render_plot, start_server
from xiplot.plots.table import Table
from xiplot.utils.auxiliary import SELECTED_COLUMN_NAME, get_selected

(
    update_table_data,
    update_selected_rows_store,
    update_lastly_activated_cell,
    update_table_columns,
) = Table.register_callbacks(dash.Dash(__name__), lambda x: x, lambda x: x)


def test_teta001_render_table(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Table")

    plot = driver.find_element(
        By.XPATH,
        "//table[@class='cell-table']",
    )

    assert "PCA 1" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teta002_select_columns(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Table")

    column_dropdown = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[2]/div",
    )
    column_dropdown.click()

    column_dropdown_input = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[2]/div/div[1]/div[1]/div[1]/div[2]/input",
    )
    column_dropdown_input.send_keys("PCA 2", Keys.RETURN)
    time.sleep(0.5)

    column_dropdown_button = driver.find_element(
        By.XPATH,
        "//button[text()='Update table']",
    )
    column_dropdown_button.click()
    time.sleep(0.5)

    plot = driver.find_element(
        By.XPATH,
        "//table[@class='cell-table']",
    )

    assert "PCA 1" not in plot.get_attribute("outerHTML")
    assert "PCA 2" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teta003_toggle_columns(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Table")

    toggle_columns = driver.find_element(
        By.XPATH,
        "//button[text()='Toggle Columns']",
    )
    toggle_columns.click()

    toggle_columns_first_checkbox = driver.find_element(
        By.XPATH, "//div[@class='show-hide-menu-item']/input"
    )
    toggle_columns_first_checkbox.click()

    plot = driver.find_element(
        By.XPATH,
        "//table[@class='cell-table']",
    )

    assert "PCA 1" not in plot.get_attribute("outerHTML")
    assert "PCA 2" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_create_table():
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    aux = pd.DataFrame({SELECTED_COLUMN_NAME: [True, True]})
    output = update_table_data(aux, [df], [[]])
    table_df = output[0][0]
    sort_by = output[1][0]

    assert table_df[0] == {"col1": 1, "col2": 3, "Selection": True}
    assert table_df[1] == {"col1": 2, "col2": 4, "Selection": True}
    assert sort_by == []


def test_update_selected_rows_store():
    aux = pd.DataFrame({SELECTED_COLUMN_NAME: [False, False]})
    output = update_selected_rows_store([[1]], aux)
    assert all(get_selected(output) == [False, True])


def test_update_table_checkbox():
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    aux = pd.DataFrame({SELECTED_COLUMN_NAME: [False, True]})
    output = update_table_data(aux, [df], [[]])
    selected_rows = output[2]

    assert selected_rows == [[1]]


def test_update_lastly_activated_cell():
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    output = update_lastly_activated_cell(
        [{"row": 1, "column_id": "col1"}], [[0, 1]], df
    )
    lastly_activated_cell_row = output["cell_store"]
    updated_active_cell = output["active_cell"]

    assert lastly_activated_cell_row == 1
    assert updated_active_cell == [None]
