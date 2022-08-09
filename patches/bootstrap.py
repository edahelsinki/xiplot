import re
import shutil

import dash
import pyodide

from pathlib import Path

from dashapp.setup import setup_dash_app


""" Bootstrap the dashapp with the data directory """


def bootstrap_dash_app(url_base_pathname):
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

    app = setup_dash_app(
        unsafe_local_server=True,
        url_base_pathname=url_base_pathname,
        compress=False,
        eager_loading=True,
    )

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
