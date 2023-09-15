from pathlib import Path
import re
import sys
from importlib.metadata import version

import dash

cwd = Path.cwd()
if (cwd / "pyproject.toml").exists():
    dist = cwd.parent / "dist"
elif (cwd / "xiplot" / "pyproject.toml").exists():
    sys.path.insert(0, "xiplot")
    dist = cwd / "dist"
elif (cwd.parent / "xiplot" / "pyproject.toml").exists():
    sys.path.insert(0, "../xiplot")
    dist = cwd.parent / "dist"
else:
    raise FileNotFoundError("Could not identify the xiplot root directory")


from xiplot.setup import setup_xiplot_dash_app


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


""" Initialise a minimal version of the xiplot dash app to run requests against """

app = setup_xiplot_dash_app(
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


"""Insert the correct version numbers into bootstrap.py"""

with open(dist.parent / "patches" / "bootstrap.py", "rt") as file:
    content = file.read()

# Packages that cannot be installed via micropip
mocked_packages = ""
for package in ["jsbeautifier"]:
    try:
        mocked_packages += f'"{package}": "{version(package)}",'
    except:
        print("Could not find version for", package)
reg = 'MOCKED_PACKAGES = (".+")'
rep = f"MOCKED_PACKAGES = {{{mocked_packages}}}"
content = re.sub(reg, rep, content)

# Packages that require a specific version, either due to bundled javascript
# files (dash, dash_*) or micropip:s rudimentary dependency resolving (flask)
required_packages = ""
for package in ["flask", "dash", "dash_extensions", "dash_mantine_components"]:
    try:
        required_packages += f'"{package}=={version(package)}",'
    except:
        print("Could not find version for", package)
reg = 'REQUIRED_PACKAGES = (".+")'
rep = f"REQUIRED_PACKAGES = [{required_packages}]"
content = re.sub(reg, rep, content)

# Packages that are loaded after xiplot has started
delayed_packages = ["scikit-learn"]
for package in ["jsonschema"]:
    try:
        delayed_packages.append(f"{package}=={version(package)}")
    except:
        print("Could not find version for", package)
delayed_packages = '"' + '","'.join(delayed_packages) + '"'
reg = 'DELAYED_PACKAGES = (".+")'
rep = f"DELAYED_PACKAGES = [{delayed_packages}]"
content = re.sub(reg, rep, content)

whl = sorted(dist.glob("xiplot-*-py3-none-any.whl"))
assert len(whl) > 0, f"Could not find the xiplot wheel in {str(dist)}"
reg = 'XIPLOT_WHEEL = "(.+)"'
rep = f'XIPLOT_WHEEL = "{whl[-1].name}"'
content = re.sub(reg, rep, content)

with open(dist / "bootstrap.py", "wt") as file:
    file.write(content)
