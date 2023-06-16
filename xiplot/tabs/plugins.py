import uuid
from asyncio import Future
from collections import defaultdict
from functools import partial
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, List, Literal, Optional, Tuple
from warnings import warn

import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, ctx, dcc, html

from xiplot.tabs import Tab
from xiplot.utils.components import FlexRow
from xiplot.utils.layouts import layout_wrapper


class Plugins(Tab):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store, plugin_dir=""):
        @app.callback(
            Output("plugin-tab-notify-container", "children"),
            Output("plugin_paths", "value"),
            Output("plugin-search-input", "value"),
            Output("plugin_paths", "options"),
            Output("plugin-tab-load-progress", "value"),
            Output("plugin-reload-button", "disabled"),
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
                    [
                        dmc.Notification(
                            id=progress_id,
                            color="green",
                            title="Success",
                            message="The plugin was successfully installed!",
                            action="update",
                            autoClose=5000,
                        ),
                        dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="yellow",
                            title="Information",
                            message=(
                                "You can now activate the newly installed"
                                " plugin by clicking the 'Reload χiplot'"
                                " button in the 'Plugins' tab."
                            ),
                            action="show",
                            autoClose=False,
                        ),
                    ],
                    dash.no_update,
                    "",
                    get_suggested_plugin_options(plugin_dir=plugin_dir),
                    "",
                    False,
                )
            if trigger == "plugin-tab-load-exception":
                exception = str(exception)
                exception = exception[exception.find("|") + 1 :]  # noqa: E203

                return (
                    dmc.Notification(
                        id=progress_id,
                        color="red",
                        title="Error",
                        message=exception,
                        action="update",
                        autoClose=False,
                    ),
                    dash.no_update,
                    "",
                    get_suggested_plugin_options(plugin_dir=plugin_dir),
                    "",
                    dash.no_update,
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
                        message="You have not selected a plugin to install.",
                        action="show",
                        autoClose=10000,
                    ),
                    dash.no_update,
                    "",
                    dash.no_update,
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
                            " finished installing."
                        ),
                        action="show",
                        autoClose=10000,
                    ),
                    dash.no_update,
                    "",
                    dash.no_update,
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
                        message="Installing the plugin",
                        action="show",
                        loading=True,
                        autoClose=False,
                        disallowClose=True,
                    ),
                    None,
                    "",
                    dash.no_update,
                    progress_id,
                    dash.no_update,
                )
            except Exception as err:
                return (
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="red",
                        title="Error",
                        message=(
                            f"Installing a plugin from '{plugin_source}'"
                            f" failed with the following error: {err}"
                        ),
                        action="show",
                        autoClose=False,
                    ),
                    None,
                    "",
                    dash.no_update,
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
            Output("plugin-reload-modal", "opened"),
            Output("plugin-reload-activations", "children"),
            Input("plugin-reload-button", "n_clicks"),
            Input("plugin-reload-accept", "n_clicks"),
            Input("plugin-reload-cancel", "n_clicks"),
            State("plugin-reload-modal", "opened"),
            prevent_initial_call=True,
        )
        def update_plugin_reload_modal(reload, accept, cancel, opened):
            if ctx.triggered_id == "plugin-reload-accept":
                import pyodide

                get_plugins_cached.cache = dict()

                pyodide.code.run_js(
                    'self.postMessage({ jsEval: "window.web_dash.reload()" })'
                )

                return dash.no_update, dash.no_update

            plugins = defaultdict(set)

            for (
                kind,
                name,
                path,
                plugin,
            ) in get_all_loaded_plugins():
                plugins[path.split(":")[0].split(".")[0]].add(kind)

            for (
                kind,
                name,
                path,
                plugin,
            ) in get_all_loaded_plugins_cached():
                plugins[path.split(":")[0].split(".")[0]].discard(kind)

            new_plugins = []

            for plugin, kinds in plugins.items():
                if len(kinds) == 0:
                    continue

                new_plugins.append(
                    dmc.ListItem(f"{plugin}: {', '.join(kinds)}")
                )

            return not opened, new_plugins

    @staticmethod
    def create_layout(plugin_dir=""):
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
                                get_suggested_plugin_options(
                                    plugin_dir=plugin_dir
                                ),
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
                                "Install",
                                id="plugin-submit-button",
                                n_clicks=0,
                                className="button",
                            ),
                        ),
                        title="Install a Plugin",
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
                                    "Check the list of activated plugins"
                                ),
                            ),
                            html.Button(
                                "Reload χiplot",
                                id="plugin-reload-button",
                                n_clicks=0,
                                className="button",
                                disabled=True,
                            ),
                            dmc.Modal(
                                title="Do you really want to reload χiplot?",
                                id="plugin-reload-modal",
                                zIndex=10000,
                                children=[
                                    dmc.Text(
                                        "Please ensure that you have"
                                        " downloaded your plots and data so"
                                        " that nothing is lost. The following"
                                        " recently installed plugins will"
                                        " become activated after the reload:"
                                    ),
                                    dmc.Space(h=10),
                                    dmc.List(
                                        [],
                                        id="plugin-reload-activations",
                                        withPadding=True,
                                    ),
                                    dmc.Space(h=20),
                                    dmc.Group(
                                        [
                                            dmc.Button(
                                                "Reload",
                                                id="plugin-reload-accept",
                                            ),
                                            dmc.Button(
                                                "Cancel",
                                                color="red",
                                                variant="outline",
                                                id="plugin-reload-cancel",
                                            ),
                                        ],
                                        position="right",
                                    ),
                                ],
                            ),
                        ),
                        title="Active Plugins",
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


def get_plugins(
    plugin_type: Literal["read", "write", "plot", "global", "callback"],
) -> List[Tuple[str, str, Any]]:
    """Get a list of all plugins of the specified type.

    Args:
        plugin_type: The type of xiplot plugin.

    Returns:
        A list of tuples of each plugin's name, path, and its
        loaded `entry_point`.
    """
    try:
        # Python 3.10+
        plugins = entry_points(group=f"xiplot.plugin.{plugin_type}")
    except TypeError:
        # Python 3.8-3.9
        plugins = entry_points().get(f"xiplot.plugin.{plugin_type}", ())

    loaded_plugins = []
    for plugin in plugins:
        try:
            loaded_plugins.append((plugin.name, plugin.value, plugin.load()))
        except Exception as e:
            warn(f"Could not load plugin {plugin}: {e}")

    return loaded_plugins


def get_plugins_cached(
    plugin_type: Literal["read", "write", "plot", "global", "callback"],
) -> List[Tuple[str, str, Any]]:
    """Get a list of all plugins of the specified type
     (this call is cached for future reuse).

    Args:
        plugin_type: The type of xiplot plugin.

    Returns:
        A list of tuples of each plugin's name, path, and its
        loaded `entry_point`.
    """
    if getattr(get_plugins_cached, "cache", None) is None:
        get_plugins_cached.cache = dict()

    cached_plugins_of_type = get_plugins_cached.cache.get(plugin_type, None)

    if cached_plugins_of_type is not None:
        return cached_plugins_of_type

    loaded_plugins = get_plugins(plugin_type)
    get_plugins_cached.cache[plugin_type] = loaded_plugins

    return loaded_plugins


def get_all_loaded_plugins() -> List[Tuple[str, str, str, Any]]:
    """Collects the list of all loaded plugins and their types.

    Returns:
        A list of tuples of each plugin's type, name, path, and its
        loaded `entry_point`.

    """
    plugins = []

    for plugin_type in ["read", "write", "plot", "global", "callback"]:
        for name, path, plugin in get_plugins(plugin_type):
            plugins.append((plugin_type, name, path, plugin))

    return plugins


def get_all_loaded_plugins_cached() -> List[Tuple[str, str, str, Any]]:
    """Collects the list of all cached loaded plugins and their types.

    Returns:
        A list of tuples of each plugin's type, name, path, and its
        loaded `entry_point`.

    """
    plugins = []

    for plugin_type in ["read", "write", "plot", "global", "callback"]:
        for name, path, plugin in get_plugins_cached(plugin_type):
            plugins.append((plugin_type, name, path, plugin))

    return plugins


def is_dynamic_plugin_loading_supported() -> bool:
    """Checks if xiplot supports dynamically loading new plugins at runtime.

    Returns:
        `True` if dynamic loading is supported, `False` otherwise.
    """
    try:
        import micropip  # noqa: F401
    except ImportError:
        return False

    return True


def get_loaded_plugin_options():
    plugins = defaultdict(set)

    for (
        kind,
        name,
        path,
        plugin,
    ) in get_all_loaded_plugins_cached():
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


def get_suggested_plugin_options(plugin_dir=""):
    return [
        {"label": fp.name, "value": str(fp)}
        for fp in get_plugin_filepaths(plugin_dir=plugin_dir)
    ]


def get_plugin_filepaths(plugin_dir=""):
    try:
        return sorted(
            (
                fp
                for fp in Path(plugin_dir).iterdir()
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
            "Installing new plugins is only supported in WASM"
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
            "Installing new plugins is only supported in WASM"
        )

    # Protect against arbitrary local installs
    if plugin_source.startswith("emfs:"):
        raise ValueError("Plugin source must be a URL or PyPi package name")

    asyncio.ensure_future(micropip.install(plugin_source)).add_done_callback(
        partial(__micropip_install_callback, try_remove_file=None)
    )


def __micropip_install_callback(
    future: Future, try_remove_file: Optional[Path]
):
    import pyodide

    result = str(uuid.uuid4())

    try:
        future.result()
        target = "success"
    except Exception as err:
        target = "exception"
        result += f"|{err}"

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
