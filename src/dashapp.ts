//@ts-ignore
window.dashApp = `
import dashapp

from dash_extensions.enrich import DashProxy, ServersideOutputTransform

from dashapp.app import DashApp
from dashapp.utils.store import ServerSideStoreBackend

app = DashProxy(
    "dashapp.app", url_base_pathname=URL_BASE_PATHNAME,
    suppress_callback_exceptions=True, compress=False, eager_loading=True,
    transforms=[ServersideOutputTransform(
        backend=ServerSideStoreBackend(), session_check=False, arg_check=False,
    )],
)


import pyodide
import shutil

from pathlib import Path

Path("data").mkdir(exist_ok=True, parents=True)

for dataset in [
    "autompg-B.csv", "autompg.csv", "auto-mpg.csv",
    "Wang-B.csv", "Wang-dataframe.csv",
]:
    with open(Path("data") / dataset, "w") as file:
        shutil.copyfileobj(pyodide.http.open_url("data/" + dataset), file)


app = DashApp(app=app, df_from_store=lambda df: df, df_to_store=lambda df: df).app

# Dummy request to ensure the server is setup when we request the index
with app.server.app_context():
    with app.server.test_client() as client:
        client.get("_favicon.ico")
`;
