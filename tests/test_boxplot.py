import dash
import pandas as pd
from selenium.webdriver.common.by import By

from tests.util_test import (
    click_pdf_button,
    render_plot,
    select_dropdown,
    start_server,
)
from xiplot.plots.boxplot import Boxplot


def test_boxplot_browser(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "boxplot")

    # Check render
    plot = driver.find_element(By.CLASS_NAME, "dash-graph")
    assert "Boxplot" in plot.get_attribute("id")
    dropdowns = driver.find_element(By.ID, "plots").find_elements(
        By.CLASS_NAME, "dash-dropdown"
    )
    assert len(dropdowns) == 8

    # Change axis
    select_dropdown(dropdowns[0], "origin")
    assert "origin" in driver.find_element(By.CLASS_NAME, "xtitle").text

    # Change color
    select_dropdown(dropdowns[4], "cylinder")
    assert "cylinder" in driver.find_element(By.CLASS_NAME, "dash-graph").text

    # Change plot
    select_dropdown(dropdowns[6], "Violin")
    select_dropdown(dropdowns[6], "Strip")

    # Download pdf
    click_pdf_button(driver)

    # Close browser
    assert dash_duo.get_logs() == [], "browser console should contain no error"
    driver.close()


def test_boxplot_create():
    render = Boxplot.register_callbacks(
        dash.Dash(__name__), lambda x: x, lambda x: x
    )

    for plot in ["Box plot", "Violin plot", "Strip chart"]:
        fig = render(
            "col1",
            "col2",
            plot,
            "Clusters",
            0,
            pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}),
            pd.DataFrame(index=range(2)),
            None,
        )
        assert str(type(fig)) == "<class 'plotly.graph_objs._figure.Figure'>"
