import time

import dash
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.util_test import render_plot, start_server
from xiplot.plots.scatterplot import Scatterplot
from xiplot.utils.auxiliary import get_clusters, get_selected

(
    tmp,
    handle_click_events,
    handle_hover_events,
    handle_cluster_drawing,
) = Scatterplot.register_callbacks(
    dash.Dash(__name__), lambda x: x, lambda x: x
)


def test_tesc001_render_scatterplot(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Scatterplot")

    plot = driver.find_element(By.CLASS_NAME, "dash-graph")

    assert "scatterplot" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_tesc002_change_axis_value(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Scatterplot")

    driver.find_element(By.CLASS_NAME, "dd-double-left").click()

    x = driver.find_element(
        By.XPATH,
        (
            "//div[@class='dd-double-left']"
            "/div[2]/div[1]/div[1]/div[1]/div[2]/input"
        ),
    )

    x.send_keys("mpg")
    x.send_keys(Keys.RETURN)
    time.sleep(0.5)

    assert "mpg" in driver.find_element(By.CLASS_NAME, "xtitle").text
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_tesc003_target_setting(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Scatterplot")

    color = driver.find_element(
        By.XPATH,
        (
            "//div[@class='plots']/div[3]/div[2]/"
            "div[1]/div[1]/div[1]/div[2]/input"
        ),
    )

    color.send_keys("PCA 1")
    color.send_keys(Keys.RETURN)
    time.sleep(0.5)

    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_tesc004_jitter_setting(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Scatterplot")

    jitter_slider = driver.find_element(By.CLASS_NAME, "rc-slider-step")
    jitter_slider.click()
    time.sleep(0.5)

    jitter_value = driver.find_element(By.CLASS_NAME, "rc-slider-handle")

    assert "0.5" in jitter_value.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"
    driver.close()


def test_create_scatterplot():
    fig = tmp(
        "col1",
        "col2",
        "Clusters",
        None,
        0,
        pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}),
        pd.DataFrame(index=range(2)),
        None,
    )
    assert str(type(fig)) == "<class 'plotly.graph_objs._figure.Figure'>"


def test_handle_click_events():
    click = [{"points": [{"customdata": [{"index": 0}]}]}]
    output = handle_click_events(click, pd.DataFrame(index=range(2)))

    aux = output["aux"]
    clicked_row = output["click_store"]
    clicked_update = output["scatter"]

    assert all(get_selected(aux) == [True, False])
    assert clicked_row == 0
    assert clicked_update == [None]


def test_handle_hover_events():
    hover = [{"points": [{"customdata": [{"index": 1}]}]}]
    output = handle_hover_events(hover)

    hovered_row = output["hover_store"]
    hover_update = output["scatter"]

    assert hovered_row == 1
    assert hover_update == [None]


def test_handle_cluster_drawing():
    selected_points = [{"points": [{"customdata": [{"index": 1}]}]}]
    aux = handle_cluster_drawing(
        selected_points, pd.DataFrame(index=range(2)), "c1", False
    )
    assert all(get_clusters(aux) == ["c2", "c1"])
