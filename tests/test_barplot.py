import time
import pandas as pd
import dash

from xiplot.setup import setup_xiplot_dash_app
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from tests.util_test import render_plot
from xiplot.plots.barplot import Barplot

tmp, update_settings = Barplot.register_callbacks(
    dash.Dash(__name__), lambda x: x, lambda x: x
)


def test_teba001_render_barplot(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Barplot")

    plot = driver.find_element(By.CLASS_NAME, "dash-graph")

    assert "barplot" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teba002_change_axis_value(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Barplot")

    driver.find_element(By.CLASS_NAME, "dd-double-left").click()

    x = driver.find_element(
        By.XPATH,
        "//div[@class='dd-double-left']/div[2]/div[1]/div[1]/div[1]/div[2]/input",
    )

    x.send_keys("model-year")
    x.send_keys(Keys.RETURN)

    time.sleep(1)

    assert "model-year" in driver.find_element(By.CLASS_NAME, "xtitle").text
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teba003_set_cluster(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Barplot")

    cluster_dd = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[4]/div[2]",
    )
    cluster_dd.click()

    time.sleep(1)

    driver.find_element(By.CLASS_NAME, "Select-menu-outer").click()

    time.sleep(1)

    assert "cluster #2" in driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[4]/div[2]/div[1]/div[1]",
    ).get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teba004_set_order(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Barplot")

    comparison_order_dd = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[5]/div[2]",
    )
    comparison_order_dd.click()

    time.sleep(1)

    dropdown_input = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[5]/div[2]/div[1]/div[1]/div[1]/div[@class='Select-input']/input",
    )
    dropdown_input.send_keys("total", Keys.RETURN)

    time.sleep(1)

    assert "total" in driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[5]/div[2]/div[1]/div[1]",
    ).get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_create_barplot():
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    output = tmp("col1", "col2", ["all"], "reldiff", ["all", "all"], df)
    fig = output[0]

    assert str(type(fig)) == "<class 'plotly.graph_objs._figure.Figure'>"
