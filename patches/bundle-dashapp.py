import hashlib
import json
import re
import toml

import dash

from pathlib import Path

from dashapp.setup import setup_dash_app


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


""" Initialise a minimal version of the dashapp to run requests against """

app = setup_dash_app(
    unsafe_local_server=True,
    compress=False,
    eager_loading=True,
)


@app.server.errorhandler(Exception)
def server_error(err):
    return str(err), 500


# Dummy request to ensure the server is setup when we request the index
with app.server.app_context():
    with app.server.test_client() as client:
        client.get("_favicon.ico")


""" Query dash for all script dependencies that must be statically bundled """

SRC_PATTERN = re.compile(r"src=\"([^\"]+)\"")
MAP_PATTERN = re.compile(r"^\/\/# sourceMappingURL=(.+)$", re.MULTILINE)

dist = Path.cwd().parent / "dist"

for script in app._generate_scripts_html().split("</script>"):
    src = SRC_PATTERN.search(script)
    if src is None:
        continue
    src = src.group(1)

    # Fetch the .js script file
    with app.server.app_context():
        with app.server.test_client() as client:
            response = client.get(src)

            if response.status_code != 200:
                raise Exception(response.text)

            content = response.text

    path = dist / src.strip("/")

    path.parent.mkdir(parents=True, exist_ok=True)

    content = MAP_PATTERN.sub(f"//# sourceMappingURL={Path(src).name}.map", content)

    with open(path, "w") as file:
        file.write(content)

    print(src)

    src_map = src + ".map"

    # Fetch the script debug .map file
    with app.server.app_context():
        with app.server.test_client() as client:
            response = client.get(src_map)

            if response.status_code != 200:
                continue

            content = response.text

    path_map = dist / src_map.strip("/")

    with open(path_map, "w") as file:
        file.write(content)

    print(src_map)


""" Register the dashapp module in the pyodide registry """

with open("pyproject.toml", "r") as file:
    pyproject = toml.load(file)

    name = pyproject["project"]["name"]
    version = pyproject["project"]["version"]
    dependencies = list(pyproject["dependencies"].keys())

with open(dist / "repodata.json", "r") as file:
    repodata = json.load(file)

with open(dist / f"{name}-{version}-py3-none-any.whl", "rb") as file:
    sha256 = hashlib.sha256(file.read()).hexdigest()

repodata["packages"][name] = {
    "name": name,
    "version": version,
    "file_name": f"{name}-{version}-py3-none-any.whl",
    "install_dir": "site",
    "sha256": sha256,
    "depends": dependencies,
    "imports": [name],
}

with open(dist / "repodata.json", "w") as file:
    json.dump(repodata, file)
