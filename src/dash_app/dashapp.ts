//@ts-ignore
window.dashApp = `
import dashapp

from dash_extensions.enrich import DashProxy, ServersideOutputTransform

from dashapp.services.dash import DashApp
from dashapp.services.store import ServerSideStoreBackend

# FIXME: hotfix until https://github.com/thedirtyfew/dash-extensions/issues/188 is fixed
import dash_extensions
dash_extensions.async_resources.remove("burger")
dash_extensions._js_dist = [ext for ext in dash_extensions._js_dist if ext["relative_package_path"] not in ["async-burger.js", "async-burger.min.js"]]

app = DashProxy(
    __name__, suppress_callback_exceptions=True, compress=False, eager_loading=True,
    transforms=[ServersideOutputTransform(
        backend=ServerSideStoreBackend(), session_check=False, arg_check=False,
    )],
)
app._favicon = "favicon.ico"


import os
import pyodide
import shutil

from pathlib import Path

os.mkdir("data")

for dataset in [
    "autompg-B.csv", "autompg.csv", "auto-mpg.data",
    "Wang-B.csv", "Wang-dataframe.csv",
]:
    with open(Path("data") / dataset, "w") as file:
        shutil.copyfileobj(pyodide.http.open_url("data/" + dataset), file)


app = DashApp(app=app).app
`;
