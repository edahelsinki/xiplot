//@ts-ignore
window.dashApp = `
import dashapp

from dash_extensions.enrich import DashProxy, ServersideOutputTransform

from dashapp.app import DashApp
from dashapp.utils.store import ServerSideStoreBackend

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
    "autompg-B.csv", "autompg.csv", "auto-mpg.csv",
    "Wang-B.csv", "Wang-dataframe.csv",
]:
    with open(Path("data") / dataset, "w") as file:
        shutil.copyfileobj(pyodide.http.open_url("data/" + dataset), file)


app = DashApp(app=app, df_from_store=lambda df: df, df_to_store=lambda df: df).app
`;
