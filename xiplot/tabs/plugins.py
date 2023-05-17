import uuid
from asyncio import Future
from collections import defaultdict
from functools import partial
from pathlib import Path
from typing import Optional

import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, ctx, dcc, html

from xiplot.plugin import get_all_loaded_plugins, get_plugins_cached
from xiplot.tabs import Tab
from xiplot.utils.components import FlexRow
from xiplot.utils.layouts import layout_wrapper


class Plugins(Tab):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store, dir_path=""):
        @app.callback(
            Output("plugin-tab-notify-container", "children"),
            Output("plugin_paths", "value"),
            Output("plugin-search-input", "value"),
            Output("loaded_plugins", "options"),
            Output("plugin-tab-load-progress", "value"),
            Input("plugin-submit-button", "n_clicks"),
            Input("plugin-tab-load-success", "value"),
            Input("plugin-tab-load-exception", "value"),
            State("plugin_paths", "value"),
            State("plugin-search-input", "value"),
            State("plugin-tab-load-progress", "value"),
        )
        def load_plugin(
            plugin_btn,
            success,
            exception,
            plugin_path,
            plugin_search,
            progress_id,
        ):
            trigger = ctx.triggered_id

            if trigger == "plugin-tab-load-success":
                return (
                    dmc.Notification(
                        id=progress_id,
                        color="green",
                        title="Success",
                        message="The plugin was successfully loaded!",
                        action="update",
                        autoClose=5000,
                    ),
                    dash.no_update,
                    "",
                    get_loaded_plugin_options(),
                    "",
                )
            if trigger == "plugin-tab-load-exception":
                return (
                    dmc.Notification(
                        id=progress_id,
                        color="red",
                        title="Error",
                        message=str(exception),
                        action="update",
                        autoClose=False,
                    ),
                    dash.no_update,
                    "",
                    get_loaded_plugin_options(),
                    "",
                )

            plugin_source = None

            if not plugin_path and plugin_search:
                plugin_source = plugin_search
                install_plugin = install_remote_plugin

            if plugin_path:
                plugin_source = plugin_path
                install_plugin = install_local_plugin

            if not plugin_source:
                return (
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message="You have not selected a plugin to load.",
                        action="show",
                        autoClose=10000,
                    ),
                    dash.no_update,
                    "",
                    dash.no_update,
                    dash.no_update,
                )

            if progress_id:
                return (
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=(
                            "Please wait until the previous plugin has"
                            " finished loading."
                        ),
                        action="show",
                        autoClose=10000,
                    ),
                    dash.no_update,
                    "",
                    dash.no_update,
                    dash.no_update,
                )

            try:
                install_plugin(plugin_source)

                progress_id = str(uuid.uuid4())

                return (
                    dmc.Notification(
                        id=progress_id,
                        color="blue",
                        title="Processing",
                        message="Loading the plugin",
                        action="show",
                        loading=True,
                        autoClose=False,
                        disallowClose=True,
                    ),
                    None,
                    "",
                    dash.no_update,
                    progress_id,
                )
            except Exception as err:
                return (
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="red",
                        title="Error",
                        message=(
                            f"Loading a plugin from '{plugin_source}'"
                            f" failed with the following error: {err}"
                        ),
                        action="show",
                        autoClose=False,
                    ),
                    None,
                    "",
                    dash.no_update,
                    dash.no_update,
                )

        @app.callback(
            Output("plugin-search-input", "value"),
            Input("plugin_paths", "search_value"),
        )
        def sync_search_input(search):
            if search == "":
                return dash.no_update
            return search

        @app.callback(
            Output("plugin_paths", "options"),
            Input("loaded_plugins", "options"),
        )
        def update_suggested_plugins(plugins):
            return [
                {"label": fp.name, "value": str(fp)}
                for fp in get_plugin_filepaths(dir_path=dir_path)
            ]

    @staticmethod
    def create_layout(dir_path=""):
        uploader = dcc.Upload(
            id="plugin_uploader",
            children=html.Div(
                # [
                #     "Drag and Drop or ",
                #     html.A("Select a Python .whl File"),
                #     " to upload",
                # ]
                "Uploading new plugins is not yet supported."
            ),
            className="dcc-upload",
            disabled=True,
        )

        return FlexRow(
            html.Div(
                [
                    layout_wrapper(
                        component=FlexRow(
                            dcc.Dropdown(
                                [
                                    {"label": fp.name, "value": str(fp)}
                                    for fp in get_plugin_filepaths(
                                        dir_path=dir_path
                                    )
                                ],
                                id="plugin_paths",
                                placeholder=(
                                    "Select a suggested plugin or type its URL"
                                    " or PyPi package name"
                                ),
                            ),
                            layout_wrapper(
                                component=dcc.Input(id="plugin-search-input"),
                                style={"display": "none"},
                            ),
                            html.Button(
                                "Load",
                                id="plugin-submit-button",
                                n_clicks=0,
                                className="button",
                            ),
                        ),
                        title="Load a Plugin",
                        css_class="dash-dropdown",
                    ),
                    html.Br(),
                    layout_wrapper(
                        component=FlexRow(
                            dcc.Dropdown(
                                get_loaded_plugin_options(),
                                id="loaded_plugins",
                                clearable=False,
                                searchable=False,
                                placeholder=(
                                    "Check the list of already loaded plugins"
                                ),
                            ),
                        ),
                        title="Loaded Plugins",
                        css_class="dash-dropdown",
                    ),
                ],
                className="stretch",
            ),
            html.Div(
                [uploader],
                id="plugin_uploader_container",
                className="dash-uploader",
            ),
            id="control_plugin_content-container",
        )

    @staticmethod
    def create_layout_globals():
        return html.Div(
            [
                html.Div(
                    id="plugin-tab-notify-container", style={"display": "none"}
                ),
                html.Div(
                    id="plugin-tab-upload-notify-container",
                    style={"display": "none"},
                ),
                dcc.Input(
                    id="plugin-tab-load-progress",
                    style={"display": "none"},
                    type="text",
                ),
                dcc.Input(
                    id="plugin-tab-load-success",
                    style={"display": "none"},
                    type="text",
                ),
                dcc.Input(
                    id="plugin-tab-load-exception",
                    style={"display": "none"},
                    type="text",
                ),
            ]
        )


def get_loaded_plugin_options():
    plugins = defaultdict(set)

    for (
        kind,
        name,
        path,
        plugin,
    ) in get_all_loaded_plugins():
        plugins[path.split(":")[0].split(".")[0]].add(kind)

    plugin_options = []

    for plugin, kinds in plugins.items():
        if len(kinds) > 0:
            kinds = f": {', '.join(kinds)}"
        else:
            kinds = ""

        plugin_options.append(
            {
                "label": f"{plugin}{kinds}",
                "value": plugin,
                "disabled": True,
            }
        )

    return plugin_options


def get_plugin_filepaths(dir_path=""):
    try:
        return sorted(
            (
                fp
                for fp in Path(dir_path).iterdir()
                if fp.is_file() and fp.suffix == ".whl"
            ),
            reverse=True,
        )

    except FileNotFoundError:
        return []


def install_local_plugin(plugin_path: str):
    import asyncio

    try:
        import micropip
    except ImportError:
        raise NotImplementedError(
            "Loading new plugins is only supported in WASM"
        )

    plugin_path = Path(plugin_path).resolve()

    asyncio.ensure_future(
        micropip.install(f"emfs:{str(plugin_path)}")
    ).add_done_callback(
        partial(__micropip_install_callback, try_remove_file=plugin_path)
    )


def install_remote_plugin(plugin_source: str):
    import asyncio

    try:
        import micropip
    except ImportError:
        raise NotImplementedError(
            "Loading new plugins is only supported in WASM"
        )

    if len(plugin_source.split()) != 1:
        raise ValueError("Plugin source must be a URL or PyPi package name")

    if (
        Path(plugin_source).exists()
        and Path(plugin_source).name != plugin_source
    ):
        raise ValueError("Plugin source must be a URL or PyPi package name")

    asyncio.ensure_future(micropip.install(plugin_source)).add_done_callback(
        partial(__micropip_install_callback, try_remove_file=None)
    )


def __micropip_install_callback(
    future: Future, try_remove_file: Optional[Path]
):
    import pyodide

    get_plugins_cached.cache = dict()

    try:
        future.result()
        target = "success"
        result = str(uuid.uuid4())
    except Exception as err:
        target = "exception"
        result = str(err)

    if target == "success" and try_remove_file is not None:
        try:
            try_remove_file.unlink()
        except Exception:
            pass

    js_callback_code = f"""
window.Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, "value",
).set.call(
    window.document.getElementById("plugin-tab-load-{target}"), {repr(result)},
);
window.document.getElementById("plugin-tab-load-{target}").dispatchEvent(
    new Event("input", {{ bubbles: true }}),
);
    """

    pyodide.code.run_js(
        f"self.postMessage({{ jsEval: {repr(js_callback_code)} }})"
    )
