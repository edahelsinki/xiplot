import uuid

import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, ctx, dcc, html

from xiplot.plugin import get_all_loaded_plugins, get_plugin_filepaths
from xiplot.tabs import Tab
from xiplot.utils.components import FlexRow
from xiplot.utils.layouts import layout_wrapper


class Plugins(Tab):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store, dir_path=""):
        @app.callback(
            Output("plugin-tab-notify-container", "children"),
            Output("plugin-search-input", "value"),
            Input("plugin-submit-button", "n_clicks"),
            State("plugin_paths", "value"),
            State("plugin-search-input", "value"),
        )
        def load_plugin(plugin_btn, plugin_path, plugin_search):
            trigger = ctx.triggered_id

            if not plugin_path and plugin_search:
                return (
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="red",
                        title="Error",
                        message=(
                            f"Loading a plugins from '{plugin_search}' using"
                            " pip is not yet supported."
                        ),
                        action="show",
                        autoClose=False,
                    ),
                    "",
                )

            if not plugin_path:
                return (
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message="You have not selected a plugin to load.",
                        action="show",
                        autoClose=10000,
                    ),
                    "",
                )

            if trigger == "plugin-submit-button":
                return (
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="red",
                        title="Error",
                        message=(
                            "Loading plugins from a file is not yet supported."
                        ),
                        action="show",
                        autoClose=False,
                    ),
                    "",
                )

            return (dash.no_update,)

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
                default_style={"minHeight": 1, "lineHeight": 4},
                disabled=True,
            )
        except (ImportError, AttributeError):
            uploader = dcc.Upload(
                id="plugin_uploader",
                children=html.Div(
                    [
                        "Drag and Drop or ",
                        html.A("Select a Python .whl File"),
                        " to upload",
                    ]
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
                                    "Select a plugin .whl file or URL or give"
                                    " its PyPi name"
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
                        title="Choose a Plugin",
                        css_class="dash-dropdown",
                    ),
                    html.Br(),
                    layout_wrapper(
                        component=FlexRow(
                            dcc.Dropdown(
                                [
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
                                ],
                                id="loaded_plugins",
                                clearable=False,
                                searchable=False,
                                placeholder="Check the loaded plugins",
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
            ]
        )
