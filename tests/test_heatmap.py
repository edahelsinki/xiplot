import dash
import pandas as pd
from selenium.webdriver.common.by import By

from tests.util_test import render_plot, start_server
from xiplot.plots.heatmap import Heatmap

render = Heatmap.register_callbacks(
    dash.Dash(__name__), lambda x: x, lambda x: x
)[0]


def test_tehe001_render_heatmap(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Heatmap")

    plot = driver.find_element(By.CLASS_NAME, "dash-graph")

    assert "heatmap" in plot.get_attribute("outerHTML")
    assert dash_duo.get_logs() == [], "browser console should contain no error"

    driver.close()


def test_create_heatmap():
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    output = render(2, ["col1", "col2"], 1, df, pd.DataFrame())
    fig = output

    assert str(type(fig)) == "<class 'plotly.graph_objs._figure.Figure'>"
