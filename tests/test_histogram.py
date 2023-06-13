import time

import dash
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.util_test import render_plot
from xiplot.plots.histogram import Histogram
from xiplot.setup import setup_xiplot_dash_app

tmp = Histogram.register_callbacks(
    dash.Dash(__name__), lambda x: x, lambda x: x
)[0]


def test_tehi001_render_histogram(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app(data_dir="data"))
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Histogram")

    plot = driver.find_element(By.CLASS_NAME, "dash-graph")

    assert "histogram" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_tehi002_set_axis(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app(data_dir="data"))
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Histogram")

    driver.find_element(By.CLASS_NAME, "dd-single").click()

    x = driver.find_element(
        By.XPATH,
        "//div[@class='dd-single']/div[2]/div[1]/div[1]/div[1]/div[2]/input",
    )

    x.send_keys("mpg")
    x.send_keys(Keys.RETURN)

    time.sleep(1)

    assert "mpg" in driver.find_element(By.CLASS_NAME, "xtitle").text
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_tehi003_clear_clusters(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app(data_dir="data"))
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Histogram")

    cluster_dd = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[3]/div[2]/div[1]/div[1]/span[1]",
    )
    cluster_dd.click()

    assert "Select..." in driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[4]/div[2]/div[1]/div[1]",
    ).get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_create_histogram():
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    output = tmp("col1", "all", ["all", "all"], df, pd.DataFrame())
    fig = output

    assert str(type(fig)) == "<class 'plotly.graph_objs._figure.Figure'>"
