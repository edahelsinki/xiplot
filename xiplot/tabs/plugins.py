import uuid

import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, ctx, dcc, html

from xiplot.plugin import (
    get_all_loaded_plugins,
    get_plugin_filepaths,
    install_local_plugin,
    install_remote_plugin,
    is_plugin_loading_supported,
)
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
            if not is_plugin_loading_supported():
                return (
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=(
                            "Loading new plugins is not supported. Please run"
                            " `pip install <plugin>` from your terminal"
                            " instead."
                        ),
                        action="show",
                        autoClose=10000,
                    ),
                    dash.no_update,
                    "",
                    dash.no_update,
                    dash.no_update,
                )

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

    @staticmethod
    def create_layout(dir_path=""):
        try:
            import dash_uploader as du

            uploader = du.Upload(
                id="plugin_uploader",
                text="Drag and Drop or Select a Python .whl File to upload",
                text_disabled=(
                    "Uploading new plugins is not supported. Please run"
                    " `pip install <plugin>` from your terminal instead."
                ),
                default_style={"minHeight": 1, "lineHeight": 4},
                disabled=True,
            )
        except (ImportError, AttributeError):
            uploader = dcc.Upload(
                id="plugin_uploader",
                children=html.Div(
                    # [
                    #     "Drag and Drop or ",
                    #     html.A("Select a Python .whl File"),
                    #     " to upload",
                    # ]
                    "Uploading new plugins is not yet supported."
                    if is_plugin_loading_supported()
                    else "Uploading new plugins is not supported."
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
                                    "Select a suggested plugin or give its URL"
                                    " or PyPi package name"
                                    if is_plugin_loading_supported()
                                    else (
                                        "Loading new plugins is not supported."
                                        " Please run `pip install <plugin>`"
                                        " from your terminal instead."
                                    )
                                ),
                                disabled=not is_plugin_loading_supported(),
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
                                disabled=not is_plugin_loading_supported(),
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
    return [
        {
            "label": f"[{kind}] {name}: {path}",
            "value": path,
            "disabled": True,
        }
        for (
            kind,
            name,
            path,
        ) in get_all_loaded_plugins()
    ]
