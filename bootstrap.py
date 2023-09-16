from pathlib import Path
import re

import pyodide
import pyodide_js
import micropip


MOCKED_PACKAGES = {"jsbeautifier": "1.14.9",}
REQUIRED_PACKAGES = ["flask==2.1.2","dash==2.6.2","dash_extensions==0.1.4","dash_mantine_components==0.10.2",]
DELAYED_PACKAGES = {'sklearn': 'scikit-learn', 'jsonschema': 'jsonschema==4.6.2'}
XIPLOT_WHEEL = "xiplot-0.4.0-py3-none-any.whl"


bootstrap_dash_app = lambda _: NotImplementedError("Call `setup_bootstrap` first!")


async def install_xiplot():
    """Install xiplot and dependencies"""
    for name, version in MOCKED_PACKAGES.items():
        micropip.add_mock_package(name, version)
    await micropip.install(["setuptools", *REQUIRED_PACKAGES, XIPLOT_WHEEL])


async def setup_bootstrap():
    """Bootstrap the xiplot dash app with the data directory"""
    global bootstrap_dash_app

    from xiplot.setup import setup_xiplot_dash_app

    def setup_dash_app(url_base_pathname):
        if not Path("data").exists():
            Path("data").mkdir(exist_ok=False, parents=True)
            for dataset in pyodide.http.open_url("assets/data.ls").read().splitlines():
                pyodide_js.FS.createLazyFile(
                    "data", dataset, "data/" + dataset, True, False
                )

        if not Path("plugins").exists():
            Path("plugins").mkdir(exist_ok=False, parents=True)
            for plugin in (
                pyodide.http.open_url("assets/plugins.ls").read().splitlines()
            ):
                pyodide_js.FS.createLazyFile(
                    "plugins", plugin, "plugins/" + plugin, True, False
                )

        app = setup_xiplot_dash_app(
            unsafe_local_server=True,
            data_dir="data",
            plugin_dir="plugins",
            url_base_pathname=url_base_pathname,
            compress=False,
            eager_loading=True,
        )

        # Asynchronously install sklearn (it will be unavailable the first couple of seconds after xiplot has loaded)
        packages = "'" + "','".join(DELAYED_PACKAGES.values()) + "'"
        modules = "import " + ",".join(DELAYED_PACKAGES.keys())
        app._inline_scripts.append(
            "setTimeout("
            + f'async () => await window.web_dash.worker_manager.executeWithAnyResponse("micropip.install({packages})", {{}},)'
            + f'.then(() => window.web_dash.worker_manager.executeWithAnyResponse("{modules}", {{}}))'
            + ", 5)"
        )

        # Dummy request to ensure the server is setup when we request the index
        with app.server.app_context():
            with app.server.test_client() as client:
                client.get("_favicon.ico")

        return app

    bootstrap_dash_app = setup_dash_app


async def monkey_patch_dash():
    """Monkey-patch dash to not use time-based fingerprints"""

    import dash

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


async def setup():
    print("Loading χiplot and dependencies")
    await install_xiplot()
    print("Loaded χiplot and dependencies")
    await monkey_patch_dash()
    print("Starting χiplot")
    await setup_bootstrap()
    print("Asynchronously loading scikit-learn")


setup()
