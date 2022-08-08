import re
import shutil

import dash
import pyodide

import dashapp

from pathlib import Path

from dash_extensions.enrich import (
    DashProxy,
    ServersideOutputTransform,
    MultiplexerTransform,
    CycleBreakerTransform,
)

from dashapp.app import DashApp
from dashapp.utils.store import ServerSideStoreBackend


""" Bootstrap the dashapp with the data directory """


def bootstrap_dash_app(url_base_pathname):
    app = DashProxy(
        "dashapp.app",
        url_base_pathname=url_base_pathname,
        suppress_callback_exceptions=True,
        compress=False,
        eager_loading=True,
        prevent_initial_callbacks=True,
        transforms=[
            MultiplexerTransform(),
            CycleBreakerTransform(),
            ServersideOutputTransform(
                backend=ServerSideStoreBackend(),
                session_check=False,
                arg_check=False,
            ),
        ],
    )

    Path("data").mkdir(exist_ok=True, parents=True)

    for dataset in [
        "autompg-B.csv",
        "autompg.csv",
        "auto-mpg.csv",
        "Wang-B.csv",
        "Wang-dataframe.csv",
        "Wang-dataframe.tar",
    ]:
        with open(Path("data") / dataset, "w") as file:
            shutil.copyfileobj(pyodide.http.open_url("data/" + dataset), file)

    app = DashApp(app=app, df_from_store=lambda df: df, df_to_store=lambda df: df).app

    # Dummy request to ensure the server is setup when we request the index
    with app.server.app_context():
        with app.server.test_client() as client:
            client.get("_favicon.ico")

    return app


""" Monkey-patch dash to not use time-based fingerprints """

cache_regex = re.compile(r"^v[\w-]+$")
version_clean = re.compile(r"[^\w-]")


def new_build_fingerprint(path, version, _hash_value):
    path_parts = path.split("/")
    filename, extension = path_parts[-1].split(".", 1)
    file_path = "/".join(path_parts[:-1] + [filename])
    v_str = re.sub(version_clean, "_", str(version))

    return f"{file_path}.v{v_str}.{extension}"


def new_check_fingerprint(path):
    path_parts = path.split("/")
    name_parts = path_parts[-1].split(".")

    # Check if the resource has a fingerprint
    if len(name_parts) > 2 and cache_regex.match(name_parts[1]):
        original_name = ".".join([name_parts[0]] + name_parts[2:])
        return "/".join(path_parts[:-1] + [original_name]), True

    return path, False


dash.fingerprint.build_fingerprint = new_build_fingerprint
dash.dash.build_fingerprint = new_build_fingerprint

dash.fingerprint.check_fingerprint = new_check_fingerprint
dash.dash.check_fingerprint = new_check_fingerprint


""" Monkey patch for dash_extensions to remove print """

import dash_extensions.enrich


def _new_get_cache_id(func, output, args, session_check=None, arg_check=True):
    all_args = [func.__name__, dash_extensions.enrich._create_callback_id(output)]
    if arg_check:
        all_args += list(args)
    if session_check:
        all_args += [dash_extensions.enrich._get_session_id()]
    return dash_extensions.enrich.hashlib.md5(
        dash_extensions.enrich.json.dumps(all_args).encode()
    ).hexdigest()


dash_extensions.enrich._get_cache_id = _new_get_cache_id
