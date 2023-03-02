import time
import pandas as pd
import dash

from xiplot.setup import setup_xiplot_dash_app
from selenium.webdriver.common.by import By


from tests.util_test import render_plot
from xiplot.plots.heatmap import Heatmap

tmp = Heatmap.register_callbacks(dash.Dash(__name__), lambda x: x, lambda x: x)[0]


def test_tehe001_render_heatmap(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_xiplot_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_plot(dash_duo, driver, "Heatmap")

    plot = driver.find_element(By.CLASS_NAME, "dash-graph")

    assert "heatmap" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_create_heatmap():
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    output = tmp(2, ["col1", "col2"], df, [])
    fig = output

    assert str(type(fig)) == "<class 'plotly.graph_objs._figure.Figure'>"
