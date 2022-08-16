import time
import pandas as pd
import dash

from dashapp.setup import setup_dash_app
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

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


def test_teta001_render_table(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Table")

    plot = driver.find_element(
        By.XPATH,
        "//table[@class='cell-table']",
    )

    assert "PCA 1" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teta002_select_columns(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Table")

    column_dropdown = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[2]/div[2]",
    )
    column_dropdown.click()

    time.sleep(1)
    column_dropdown_input = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/input",
    )
    column_dropdown_input.send_keys("PCA 2", Keys.RETURN)
    time.sleep(1)

    column_dropdown_button = driver.find_element(
        By.XPATH,
        "//button[text()='Select']",
    )
    column_dropdown_button.click()
    time.sleep(1)

    plot = driver.find_element(
        By.XPATH,
        "//table[@class='cell-table']",
    )

    assert "PCA 1" not in plot.get_attribute("outerHTML")
    assert "PCA 2" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teta003_toggle_columns(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Table")

    toggle_columns = driver.find_element(
        By.XPATH,
        "//button[text()='Toggle Columns']",
    )
    toggle_columns.click()
    time.sleep(1)

    toggle_columns_first_checkbox = driver.find_element(
        By.XPATH, "//div[@class='show-hide-menu-item']/input"
    )
    toggle_columns_first_checkbox.click()
    time.sleep(1)

    plot = driver.find_element(
        By.XPATH,
        "//table[@class='cell-table']",
    )

    assert "PCA 1" not in plot.get_attribute("outerHTML")
    assert "PCA 2" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_create_table():
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


def test_add_matching_values():
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    output = add_matching_values(
        [1], [[]], ["col.*"], [["col1", "col2"]], df, ["all", "all"]
    )
    selected_columns_options = output[0][0]
    selected_columns_values = output[1][0]
    update_search_value = output[2][0]

    assert selected_columns_options == ["col.* (regex)"]
    assert selected_columns_values == ["col.* (regex)"]
    assert update_search_value is None
