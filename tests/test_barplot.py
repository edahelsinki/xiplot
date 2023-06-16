import time

import dash
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.util_test import render_plot
from xiplot.plots.barplot import Barplot
from xiplot.setup import setup_xiplot_dash_app

tmp = Barplot.register_callbacks(
    dash.Dash(__name__), lambda x: x, lambda x: x
)[0]


def test_teba001_render_barplot(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app(data_dir="data"))
    time.sleep(0.1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Barplot")

    plot = driver.find_element(By.CLASS_NAME, "dash-graph")

    assert "barplot" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teba002_change_axis_value(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app(data_dir="data"))
    time.sleep(0.1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Barplot")

    driver.find_element(By.CLASS_NAME, "dd-double-left").click()

    x = driver.find_element(
        By.XPATH,
        (
            "//div[@class='dd-double-left']"
            "/div[2]/div[1]/div[1]/div[1]/div[2]/input"
        ),
    )

    x.send_keys("model-year")
    x.send_keys(Keys.RETURN)

    time.sleep(0.1)

    assert "model-year" in driver.find_element(By.CLASS_NAME, "xtitle").text
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


# def test_teba003_set_cluster(dash_duo):
#     driver = dash_duo.driver
#     dash_duo.start_server(setup_xiplot_dash_app(data_dir="data"))
#     time.sleep(.1)
#     dash_duo.wait_for_page()

#     render_plot(dash_duo, driver, "Barplot")

#     cluster_dd = driver.find_element(
#         By.XPATH,
#         "//div[@class='dd-single cluster-comparison']/div[2]",
#     )
#     cluster_dd.click()

#     # TODO create clusters first!

#     time.sleep(.1)

#     driver.find_element(
#         By.XPATH,
#         "//div[@class='ReactVirtualized__Grid__innerScrollContainer']/div[3]",
#     ).click()

#     time.sleep(.1)

#     cluster_value = driver.find_element(
#         By.XPATH,
#         "//div[@class='dd-single cluster-comparison']/div[2]/div[1]/div[1]",
#     ).get_attribute("outerHTML")

#     assert "cluster #2" in cluster_value
#     assert dash_duo.get_logs() == [], "browser console should contain no error"

#     driver.close()


def test_teba004_set_order(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app(data_dir="data"))
    time.sleep(0.1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Barplot")

    comparison_order_dd = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[5]/div[2]",
    )
    comparison_order_dd.click()

    time.sleep(0.1)

    dropdown_input = driver.find_element(
        By.XPATH,
        (
            "//div[@class='plots']/div[4]/div[2]/div[1]/div[1]/div[1]/"
            "div[@class='Select-input']/input"
        ),
    )
    dropdown_input.send_keys("total", Keys.RETURN)

    time.sleep(0.1)

    assert "total" in driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[4]/div[2]/div[1]/div[1]",
    ).get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_create_barplot():
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    output = tmp("col1", "col2", ["all"], "reldiff", df, pd.DataFrame())
    fig = output[0]
    assert str(type(fig)) == "<class 'plotly.graph_objs._figure.Figure'>"
