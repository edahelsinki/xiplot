import dash
import pandas as pd
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.util_test import render_plot, start_server
from xiplot.plots.smiles import Smiles

update_smiles = Smiles.register_callbacks(
    dash.Dash(__name__), lambda x: x, lambda x: x
)


@pytest.fixture
def driver(dash_duo):
    driver = start_server(dash_duo)
    render_plot(dash_duo, driver, "Smiles")
    return driver


def test_tesm001_render_smiles(dash_duo, driver):
    plot = driver.find_element(By.XPATH, "//div[@class='plots']")
    assert Smiles.get_id(None, "display")["type"] in plot.get_attribute(
        "innerHTML"
    )
    assert dash_duo.get_logs() == [], "browser console should contain no error"


def test_tesm002_input_smiles_string(driver):
    smiles_input = driver.find_element(
        By.XPATH, "//div[@class='dash-input']/div/input"
    )
    smiles_input.clear()
    smiles_input.send_keys("O", Keys.RETURN)

    smiles_img = (
        driver.find_element(By.CLASS_NAME, "plots")
        .find_element(By.TAG_NAME, "img")
        .get_attribute("outerHTML")
    )
    svg = 'src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0naXNvLTg4NTktMSc/PiA8c3ZnIHZlcnNpb249JzEuMScgYmFzZVByb2ZpbGU9J2Z1bGwnIHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZycgeG1sbnM6cmRraXQ9J2h0dHA6Ly93d3cucmRraXQub3JnL3htbCcgeG1sbnM6eGxpbms9J2h0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsnIHhtbDpzcGFjZT0ncHJlc2VydmUnIHdpZHRoPScyNTBweCcgaGVpZ2h0PScyMDBweCcgdmlld0JveD0nMCAwIDI1MCAyMDAnPiA8IS0tIEVORCBPRiBIRUFERVIgLS0+IDxwYXRoIGNsYXNzPSdhdG9tLTAnIGQ9J00gOTIuMSA3OC45IEwgOTYuMCA3OC45IEwgOTYuMCA5MS4wIEwgMTEwLjUgOTEuMCBMIDExMC41IDc4LjkgTCAxMTQuMyA3OC45IEwgMTE0LjMgMTA3LjIgTCAxMTAuNSAxMDcuMiBMIDExMC41IDk0LjIgTCA5Ni4wIDk0LjIgTCA5Ni4wIDEwNy4yIEwgOTIuMSAxMDcuMiBMIDkyLjEgNzguOSAnIGZpbGw9JyNGRjAwMDAnLz4gPHBhdGggY2xhc3M9J2F0b20tMCcgZD0nTSAxMTcuNyAxMDYuMiBRIDExOC40IDEwNC41LCAxMjAuMSAxMDMuNSBRIDEyMS43IDEwMi41LCAxMjQuMCAxMDIuNSBRIDEyNi44IDEwMi41LCAxMjguNCAxMDQuMCBRIDEzMC4wIDEwNS42LCAxMzAuMCAxMDguMyBRIDEzMC4wIDExMS4xLCAxMjcuOSAxMTMuNiBRIDEyNS45IDExNi4yLCAxMjEuNyAxMTkuMyBMIDEzMC4zIDExOS4zIEwgMTMwLjMgMTIxLjQgTCAxMTcuNyAxMjEuNCBMIDExNy43IDExOS42IFEgMTIxLjIgMTE3LjEsIDEyMy4yIDExNS4zIFEgMTI1LjMgMTEzLjUsIDEyNi4zIDExMS44IFEgMTI3LjMgMTEwLjEsIDEyNy4zIDEwOC40IFEgMTI3LjMgMTA2LjYsIDEyNi40IDEwNS42IFEgMTI1LjUgMTA0LjYsIDEyNC4wIDEwNC42IFEgMTIyLjUgMTA0LjYsIDEyMS41IDEwNS4yIFEgMTIwLjUgMTA1LjgsIDExOS44IDEwNy4yIEwgMTE3LjcgMTA2LjIgJyBmaWxsPScjRkYwMDAwJy8+IDxwYXRoIGNsYXNzPSdhdG9tLTAnIGQ9J00gMTMxLjkgOTMuMCBRIDEzMS45IDg2LjIsIDEzNS4yIDgyLjQgUSAxMzguNiA3OC42LCAxNDQuOSA3OC42IFEgMTUxLjEgNzguNiwgMTU0LjUgODIuNCBRIDE1Ny45IDg2LjIsIDE1Ny45IDkzLjAgUSAxNTcuOSA5OS45LCAxNTQuNSAxMDMuOCBRIDE1MS4xIDEwNy43LCAxNDQuOSAxMDcuNyBRIDEzOC42IDEwNy43LCAxMzUuMiAxMDMuOCBRIDEzMS45IDk5LjksIDEzMS45IDkzLjAgTSAxNDQuOSAxMDQuNSBRIDE0OS4yIDEwNC41LCAxNTEuNSAxMDEuNiBRIDE1My45IDk4LjcsIDE1My45IDkzLjAgUSAxNTMuOSA4Ny40LCAxNTEuNSA4NC42IFEgMTQ5LjIgODEuOCwgMTQ0LjkgODEuOCBRIDE0MC41IDgxLjgsIDEzOC4yIDg0LjYgUSAxMzUuOSA4Ny40LCAxMzUuOSA5My4wIFEgMTM1LjkgOTguNywgMTM4LjIgMTAxLjYgUSAxNDAuNSAxMDQuNSwgMTQ0LjkgMTA0LjUgJyBmaWxsPScjRkYwMDAwJy8+IDwvc3ZnPiA="'  # noqa: E501

    assert svg in smiles_img


def test_render_clicks():
    d = {"col1": [1, 2], "col2": [3, 4], "smiles": ["O", "N"]}
    df = pd.DataFrame(data=d)
    smiles_string = update_smiles(1, None, "Click", "smiles", "", df)
    assert smiles_string == "N"


def test_render_hovered():
    d = {"col1": [1, 2], "col2": [3, 4], "smiles": ["O", "N"]}
    df = pd.DataFrame(data=d)
    smiles_string = update_smiles(None, 1, "Hover", "smiles", "", df)
    assert smiles_string == "N"
