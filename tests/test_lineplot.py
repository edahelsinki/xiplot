import time

import dash
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.util_test import render_plot, start_server
from xiplot.plots.lineplot import Lineplot
from xiplot.utils.auxiliary import get_selected

(
    tmp,
    handle_hover_events,
    handle_click_events,
) = Lineplot.register_callbacks(dash.Dash(__name__), lambda x: x, lambda x: x)


def test_lineplot_browser(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Lineplot")

    # Check render
    plot = driver.find_element(By.CLASS_NAME, "dash-graph")
    assert "Lineplot" in plot.get_attribute("outerHTML")
    dropdowns = driver.find_element(By.ID, "plots").find_elements(
        By.CLASS_NAME, "dash-dropdown"
    )
    assert len(dropdowns) == 6

    # Change axis
    dropdowns[0].click()
    x = dropdowns[0].find_element(
        By.XPATH, "//div[2]/div[1]/div[1]/div[1]/div[2]/input"
    )
    x.send_keys("mpg")
    x.send_keys(Keys.RETURN)
    time.sleep(0.5)
    assert "mpg" in driver.find_element(By.CLASS_NAME, "xtitle").text

    # Change color
    dropdowns[4].click()
    color = dropdowns[4].find_element(
        By.XPATH, "//div[2]/div[1]/div[1]/div[1]/div[2]/input"
    )
    color.send_keys("cylinders")
    color.send_keys(Keys.RETURN)
    time.sleep(0.5)
    assert "cylinders" in driver.find_element(By.CLASS_NAME, "dash-graph").text

    # Close browser
    assert dash_duo.get_logs() == [], "browser console should contain no error"
    driver.close()


def test_lineplot_create():
    fig = tmp(
        "col1",
        "col2",
        "Clusters",
        0,
        pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}),
        pd.DataFrame(index=range(2)),
        None,
    )
    assert str(type(fig)) == "<class 'plotly.graph_objs._figure.Figure'>"


def test_lineplot_click():
    click = [{"points": [{"customdata": [0]}]}]
    aux, row = handle_click_events(click, pd.DataFrame(index=range(2)))

    assert all(get_selected(aux) == [True, False])
    assert row == 0


def test_lineplot_hover():
    hover = [{"points": [{"customdata": [1]}]}]
    assert handle_hover_events(hover) == 1
