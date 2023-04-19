# [&chi;iplot](https://github.com/edahelsinki/xiplot) WASM WebDash version &emsp; [![CI Status]][workflow]

[CI Status]: https://img.shields.io/github/actions/workflow/status/edahelsinki/xiplot/gh-pages.yaml?branch=wasm&label=gh-pages
[workflow]: https://github.com/edahelsinki/xiplot/actions/workflows/gh-pages.yaml?query=branch%3Awasm

The WASM WebDash version of [`xiplot`](https://github.com/edahelsinki/xiplot) enables the data analysis playground to run entirely in the browser, i.e. without requiring a non-static server. Hence, the playground can be deployed as a static web app to [GitHub pages](https://www.edahelsinki.fi/xiplot).

## Technical Background

The [`xiplot`](https://github.com/edahelsinki/xiplot) playground is written in Python using plotly's [`dash`](https://github.com/plotly/dash) library to provide interactive data visualisation. Usually, `dash` requires a deployed `flask` server, on which the data processing is then run.

[`pyodide`](https://github.com/pyodide/pyodide) is a Python distribution that runs directly in the browser. It is built on `Cython`, which is then compiled to `WASM`, a standardised bytecode format, which can be run at near native speeds in modern browser. While `pyodide` can run any pure Python package, and also ships several popular Python libraries such as `numpy`, `matplotlib`, and `pandas`.

[`WebDash`](https://github.com/ibdafna/webdash) is a (research) project started by [Itay Dafna](https://github.com/ibdafna) whilst working at Bloomberg LP, with some technical mentorship from Paul Ivanov. It created a proof of concept to combining `dash` with `pyodide` by running `dash`'s `flask` server in the clientside browser using `pyodide` and intercepting `fetch` requests from the `dash` JS frontend to forward them to this virtual server. Most of this project is based on `WebDash` but provides some small improvements to make it less reliant on hardcoding the communication patterns between `dash`'s frontend and backend. While the `xiplot` WASM version primarily aims to bring `xiplot` to WASM, it can also be seen as an improved baseline to build similar ports on.

## Code structure

The [`main`](https://github.com/edahelsinki/xiplot/tree/main) branch of the repository contains the Python implementation of the `xiplot` playground. Please see its [README](https://github.com/edahelsinki/xiplot/blob/main/README.md) for more information on the organisation of the `xiplot` module.

The [`wasm`](https://github.com/edahelsinki/xiplot/tree/wasm) branch of the repository is structured as follows:
* The `xiplot` submodule pins the version of `xiplot` that the WASM WebDash version was last built with.
* The `patches` directory contains patches that are applied to `xiplot` during the building process. In particular,
  * `bootstrap.py` is a `__main__.py`-like file which is loaded by the WASM WebDash app on startup to bootstrap the initialisation of the `dash` app. It has to import the main application module, `xiplot` in our case, and define a `bootstrap_dash_app` function, similar to this one:
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
    The functionality of this `bootstrap.py` script should closely follow [`__main__.py`](https://github.com/edahelsinki/xiplot/blob/main/xiplot/__main__.py), which is used to bootstrap the Python version of the `xiplot` playground.
  * `bundle-dash-app.py` is used during the WASM WebDash build process. Its first function is to query the `xiplot` dash app for static dependencies that will need to be shipped inside the `dist` folder. Secondly, it also injects the current version numbers into `dist/bootstrap.py`.
* The `src` directory contains the implementation of the WASM WebDash bootstrapper, and is largely based on the [`WebDash`](https://github.com/ibdafna/webdash) project. It contains:
  * `index.html` is a minimal loading page which displays some progress updates as `pyodide` and the `xiplot` dash app are loaded
  * `webdash.ts` implements the entry point and bootstrapping process for WebDash. In particular, it is responsible for transitioning the web page to the dashboard once the dash app has been loaded.
  * `webflask.ts` is responsible for intercepting `fetch` requests to the `flask` server and redirecting them to the virtual one instead. In this capacity, it generates the Python code to execute the requests, and translates requests and responses between JS and Python.
  * `manager.ts` manages the communication between the `webdash.ts` and `webflask.ts` on the frontend, and the `pyodide` backend running inside a web worker.
  * `worker.ts` implements the web worker which executes Python code inside `pyodide` to simulate the virtual `flask` server inside the client's browser. To update to a newer version of `pyodide`, change URL at the top of the file.
* The `Makefile` orchestrates building the WASM WebDash version of `xiplot`. Important `make` commands include:
  * `make nuke` removes **all** build artifacts, including `pyodide`'s, allowing for a clean rebuild
  * `make clean` removes `xiplot`'s build artifacts as well as the final `dist` output folder
  * `make deploy` builds `xiplot` and prepares the `dist` folder. Use `make -B deploy` to force a rebuild.
  * `make run` wraps `make deploy` and starts a simple static `python3 -m http.server` inside the `dist` folder after building has completed.
* `package.json` and `package-lock.json` define the `npm` dependencies used to build the WASM WebDash HTML bootstrapper.

## Funding

The WASM WebDash version of the `xiplot` playground was created by [Juniper Tyree](https://github.com/juntyr) as part of their summer internship in Kai Puolamäki's [Exploratory Data Analysis group](https://github.com/edahelsinki) at the University of Helsinki. This internship was paid for by "Future Makers Funding Program 2018 of the Technology Industries of Finland Centennial Foundation, and the Jane and Aatos Erkko Foundation", with funding associated with the Atmospheric AI programme of the Finnish Center for Artificial Intelligence.

## License

* The [`src`](src) directory on the `wasm` branch is licensed under both the BSD 3-Clause License ([`LICENSE-BSD3`](LICENSE-BSD3) or https://opensource.org/licenses/BSD-3-Clause) **and** the MIT License ([`LICENSE-MIT`](LICENSE-MIT) or http://opensource.org/licenses/MIT).

* The remainder of the repository, including importantly the `xiplot` submodule, which pins the `main` branch of this repository and contains the implementation of the `xiplot` playground, is licensed under the MIT License ([`LICENSE-MIT`](LICENSE-MIT) or http://opensource.org/licenses/MIT).

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you shall be licensed as described above, without any additional terms or conditions.
