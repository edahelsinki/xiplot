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

from dash import Dash

import dashapp
from dashapp.services.dash import DashApp


dash = Dash(
    __name__, suppress_callback_exceptions=True, compress=False, eager_loading=True
)
app = DashApp(app=dash).app

import re

from pathlib import Path

SRC_PATTERN = re.compile(r"src=\"([^\"]+)\"")

for script in app._generate_scripts_html().split("\n"):
    src = SRC_PATTERN.search(script).group(1)

    print(script)

    with app.server.app_context():
        with app.server.test_client() as client:
            content = client.get(src).text

    path = Path.cwd().parent / "dist" / src.strip("/")

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as file:
        file.write(content)
