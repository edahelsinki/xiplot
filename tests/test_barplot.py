import time

import dash
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.util_test import render_plot, start_server
from xiplot.plots.barplot import Barplot

render = Barplot.register_callbacks(
    dash.Dash(__name__), lambda x: x, lambda x: x
)[0]


def test_teba001_render_barplot(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Barplot")

    plot = driver.find_element(By.CLASS_NAME, "dash-graph")

    assert "barplot" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teba002_change_axis_value(dash_duo):
    driver = start_server(dash_duo)
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
    time.sleep(0.5)

    assert "model-year" in driver.find_element(By.CLASS_NAME, "xtitle").text
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_teba003_set_cluster(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Barplot")

    # Run clustering
    driver.find_element(By.XPATH, "//div[@id='control-tabs']/div[3]").click()
    feature_dd = driver.find_element(By.ID, "cluster_feature")
    feature_dd.find_element(By.TAG_NAME, "input").send_keys("PCA")
    time.sleep(0.1)
    # The headless driver uses some wierd window size so that the dropdown
    # obscures the button. This is why we have cannot just use `click` here:
    driver.execute_script(
        "arguments[0].click();",
        driver.find_element(By.ID, "add_by_keyword-button"),
    )
    time.sleep(0.1)
    driver.find_element(By.ID, "cluster-button").click()
    time.sleep(0.5)

    # Use clusters
    inp = driver.find_element(
        By.CSS_SELECTOR, ".dd-single.cluster-comparison input"
    )
    inp.send_keys("2")
    inp.send_keys(Keys.RETURN)
    time.sleep(0.5)
    try:
        cluster_val = driver.find_element(
            By.CSS_SELECTOR, ".dd-single.cluster-comparison"
        ).find_element(By.CSS_SELECTOR, ".Select-value")
    except Exception:
        # Sometimes the GitHub test is too slow to find ".Select-value"
        cluster_val = driver.find_element(
            By.CSS_SELECTOR, ".dd-single.cluster-comparison"
        )
    assert "Cluster #2" in cluster_val.get_attribute("innerHTML")

    assert dash_duo.get_logs() == [], "browser console should contain no error"
    driver.close()


def test_teba004_set_order(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Barplot")

    comparison_order_dd = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[5]/div[2]",
    )
    comparison_order_dd.click()

    dropdown_input = driver.find_element(
        By.XPATH,
        (
            "//div[@class='plots']/div[4]/div[2]/div[1]/div[1]/div[1]/"
            "div[@class='Select-input']/input"
        ),
    )
    dropdown_input.send_keys("total", Keys.RETURN)
    time.sleep(0.5)

    assert "total" in driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[4]/div[2]/div[1]/div[1]",
    ).get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_create_barplot():
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    output = render("col1", "col2", ["all"], "reldiff", 1, df, pd.DataFrame())
    fig = output[0]
    assert str(type(fig)) == "<class 'plotly.graph_objs._figure.Figure'>"
