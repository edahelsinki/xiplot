import dash

import re

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

import dashapp

from dash_extensions.enrich import DashProxy, ServersideOutputTransform

from dashapp.services.dash import DashApp
from dashapp.services.store import ServerSideStoreBackend


dash = DashProxy(
    __name__,
    suppress_callback_exceptions=True,
    compress=False,
    eager_loading=True,
    transforms=[
        ServersideOutputTransform(
            backend=ServerSideStoreBackend(),
            session_check=False,
            arg_check=False,
        )
    ],
)
app = DashApp(app=dash).app


# FIXME: hotfix until https://github.com/thedirtyfew/dash-extensions/issues/188 is fixed
import dash_extensions

dash_extensions.async_resources.remove("burger")
dash_extensions._js_dist = [
    ext
    for ext in dash_extensions._js_dist
    if ext["relative_package_path"] not in ["async-burger.js", "async-burger.min.js"]
]


import re

from pathlib import Path

SRC_PATTERN = re.compile(r"src=\"([^\"]+)\"")

dist = Path.cwd().parent / "dist"

for script in app._generate_scripts_html().split("\n"):
    src = SRC_PATTERN.search(script).group(1)

    print(src)

    with app.server.app_context():
        with app.server.test_client() as client:
            content = client.get(src).text

    path = dist / src.strip("/")

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as file:
        file.write(content)

    try:
        src_map = src + ".map"

        with app.server.app_context():
            with app.server.test_client() as client:
                content = client.get(src_map).text

        path_map = dist / src_map.strip("/")

        with open(path_map, "w") as file:
            file.write(content)

        print(src_map)
    except:
        pass


import hashlib
import json

with open(dist / "repodata.json", "r") as file:
    repodata = json.load(file)

with open(dist / "dashapp-0.1.0-py3-none-any.whl", "rb") as file:
    sha256 = hashlib.sha256(file.read()).hexdigest()

repodata["packages"]["dashapp"] = {
    "name": "dashapp",
    "version": "0.1.0",
    "file_name": "dashapp-0.1.0-py3-none-any.whl",
    "install_dir": "site",
    "sha256": sha256,
    "depends": [
        "dash",
        "plotly",
        "dash-extensions",
        "flask",
        "pandas",
        "sklearn",
        "matplotlib",
    ],
    "imports": ["dashapp"],
}

with open(dist / "repodata.json", "w") as file:
    json.dump(repodata, file)
