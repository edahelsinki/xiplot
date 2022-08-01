# dash_app2022 WASM WebDash version &emsp; [![CI Status]][workflow]

[CI Status]: https://img.shields.io/github/checks-status/edahelsinki/dash_app2022/wasm?label=gh-pages
[workflow]: https://github.com/edahelsinki/dash_app2022/actions/workflows/gh-pages.yaml?query=branch%3Awasm

The WASM WebDash version of [`dash_app2022`](https://github.com/edahelsinki/dash_app2022) enables the data analysis playground to run entirely in the browser, i.e. without requiring a non-static server. This allows us to deploy the playground to [GitHub pages](https://www.edahelsinki.fi/dash_app2022).

## Technical Background

The [`dash_app2022`](https://github.com/edahelsinki/dash_app2022) playground is written in Python using plotly's [`dash`](https://github.com/plotly/dash) library to provide interactive data visualisation. Usually, `dash` requires a deployed `flask` server, on which the data processing is then run.

[`pyodide`](https://github.com/pyodide/pyodide) is a Python distribution that runs directly in the browser. It is built on `Cython`, which is then compiled to `WASM`, a standardised bytecode format, which can be run at near native speeds in modern browser. While `pyodide` can run any pure Python package, and also ships several popular Python libraries such as `numpy`, `matplotlib`, and `pandas`, there are many modules that have non-Python dependencies which have not yet been ported by the `pyodide` project. However, some simple modules can be ported easily by building `pyodide` from source and including these modules in the build process.

[`WebDash`](https://github.com/ibdafna/webdash) is a (research) project started by [Itay Dafna](https://github.com/ibdafna) whilst working at Bloomberg LP, with some technical mentorship from Paul Ivanov. It created a proof of concept to combining `dash` with `pyodide` by running `dash`'s `flask` server in the clientside browser using `pyodide` and intercepting `fetch` requests from the `dash` JS frontend to forward them to this virtual server. Most of this project is based on `WebDash` but provides some small improvements to make it less reliant on hardcoding the communication patterns between `dash`'s frontend and backend. While the `dash_app2022` WASM version primarily aims to bring the `dash_app2022` playground to WASM, it can also be seen as an improved baseline to build similar ports on.

## Code structure

The [`main`](https://github.com/edahelsinki/dash_app2022/tree/main) branch of the repository contains the Python implementation of the `dash_app2022` playground. Please see its [README](https://github.com/edahelsinki/dash_app2022/blob/main/README.md) for more information on the organisation of the `dashapp` module.

The [`wasm`](https://github.com/edahelsinki/dash_app2022/tree/wasm) branch of the repository is structured as follows:
* The `dashapp` submodule pins the version of the `dash_app2022` playground that the WASM WebDash version was last built with.
* The `pyodide` submodule, which is not part of this project, pins the version of `pyodide` that the WASM WebDash version was last built with. Only update this submodule once you have confirmed that the WASM WebDash version works with the new version. Only update this submodule once you have confirmed that the WASM WebDash version works with the new version.
* The `patches` directory contains patches that are applied to `pyodide` and the `dashapp` during the building process. In particular,
  * `pyodide.patch` is a git patch that includes Python modules which `dashapp` relies on in `pyodide`'s own build process. To include new packages
    1. Clean `pyodide` and apply the existing patches:
       ```shell
       make clean
       cd pyodide
       git apply --whitespace=nowarn ../patches/pyodide.patch
       ```
    2. Follow the steps described in https://pyodide.org/en/stable/development/new-packages.html to add a new package. At the time of writing, this often consists of:
       ```shell
       ./run_docker
       python -m pyodide_build mkpkg [PACKAGE]
       cd packages/[PACKAGE]
       python -m pyodide_build buildpkg meta.yaml
       ```
    3. If the building process succeeded, create the updated patch file:
       ```shell
       git add packages
       git diff --cached > ../patches/pyodide.patch
       ```
    4. Next, you need to update the following command in the [`Makefile`](https://github.com/edahelsinki/dash_app2022/blob/wasm/Makefile) to include your packages in the build process:
       https://github.com/edahelsinki/dash_app2022/blob/67d26cdceea0b436c94ec9ee72e3466eb4f6d72a/Makefile#L19
    5. Make sure that the new packages are also listed in `dashapp`'s [`pyproject.toml`](https://github.com/edahelsinki/dash_app2022/blob/main/pyproject.toml) and [`requirements.txt`](https://github.com/edahelsinki/dash_app2022/blob/main/requirements.txt) files.
    6. Finally, you can rebuild the WASM WebDash version:
       ```shell
       make -B deploy
       ```
  * `bootstrap.py` is a `__main__.py`-like file which is loaded by the WASM WebDash app on startup to bootstrap the initialisation of the `dash` app. It has to import the main application module, `dashapp` in our case, and define a `bootstrap_dash_app` function, similar to this one:
    ```python
    def bootstrap_dash_app(url_base_pathname: str) -> dash.Dash:
        ...
        app = Dash(..., url_base_pathname=url_base_pathname, eager_loading=True, ...)
        ...
        # Dummy request to ensure the server is setup when we request the index
        with app.server.app_context():
            with app.server.test_client() as client:
                client.get("_favicon.ico")
        ...
        return app
    ```
    The functionality of this `bootstrap.py` script should closely follow [`__main__.py`](https://github.com/edahelsinki/dash_app2022/blob/main/dashapp/__main__.py), which is used to bootstrap the Python version of the `dash_app2022` playground.
* The `src` directory contains the implementation of the WASM WebDash bootstrapper, and is largely based on the [`WebDash`](https://github.com/ibdafna/webdash) project. It contains:
  * `index.html` is a minimal loading page which displays some progress updates as `pyodide` and the dash app are loaded
  * `webdash.ts` implements the entry point and bootstrapping process for WebDash. In particular, it is responsible for transitioning the web page to the dashboard once the dash app has been loaded.
  * `webflask.ts` is responsible for intercepting `fetch` requests to the `flask` server and redirecting them to the virtual one instead. In this capacity, it generates the Python code to execute the requests, and translates requests and responses between JS and Python.
  * `manager.ts` manages the communication between the `webdash.ts` and `webflask.ts` on the frontend, and the `pyodide` backend running inside a web worker.
  * `worker.ts` implements the web worker which executes Python code inside `pyodide` to simulate the virtual `flask` server inside the client's browser.
* The `Makefile` orchestrates building the WASM WebDash version of `dash_app2022`. Important `make` commands include:
  * `make nuke` removes **all** build artifacts, including `pyodide`'s, allowing for a clean rebuild
  * `make clean` removes `dashapp`'s build artifacts as well as the final `dist` output folder
  * `make deploy` builds `pyodide` and `dashapp` and bundles them inside the `dist` folder. Use `make -B deploy` to force a rebuild.
  * `make run` wraps `make deploy` and starts a simple static `python3 -m http.server` inside the `dist` folder after building has completed.
* `package.json` and `package-lock.json` define the `npm` dependencies used to build the WASM WebDash HTML bootstrapper.

## License

* The [`src`](https://github.com/edahelsinki/dash_app2022/tree/wasm/src) directory on the `wasm` branch is licensed under the BSD 3-Clause License ([`LICENSE-BSD3`](LICENSE-BSD3) or https://opensource.org/licenses/BSD-3-Clause).

* The `pyodide` submodule, which is not part of this project, but whose version is pinned, is licensed under the [Mozilla Public License Version 2.0](https://choosealicense.com/licenses/mpl-2.0/).

* The remainder of the repository, including importantly the `dashapp` submodule, which pins the `main` branch of this repository and contains the implementation of the `dash_app2022` playground, is licensed under the MIT License ([`LICENSE-MIT`](LICENSE-MIT) or http://opensource.org/licenses/MIT).

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you shall be licensed as described above, without any additional terms or conditions.
