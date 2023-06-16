from collections import defaultdict

import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash, Input, Output, State, dcc, html

from xiplot.tabs import Tab
from xiplot.tabs.plugins import (
    get_all_loaded_plugins_cached,
    is_dynamic_plugin_loading_supported,
)
from xiplot.utils.components import FlexRow
from xiplot.utils.layouts import layout_wrapper


class Settings(Tab):
    @staticmethod
    def register_callbacks(app: Dash, df_from_store, df_to_store):
        pio.templates["xiplot_light"] = go.layout.Template(
            layout={
                "paper_bgcolor": "rgba(255,255,255,0)",
                "margin": dict(l=10, r=10, t=10, b=10, autoexpand=True),
                "uirevision": True,
            }
        )
        pio.templates["xiplot_dark"] = go.layout.Template(
            layout={
                "paper_bgcolor": "rgba(0,0,0,0)",
                "margin": dict(l=10, r=10, t=10, b=10, autoexpand=True),
                "uirevision": True,
            }
        )
        pio.templates.default = "plotly_white+xiplot_light"

        app.clientside_callback(
            """
function toggleLightDarkMode(clicks, data) {
    if (clicks != undefined) {
        data = !data
    }
    if (data) {
        document.documentElement.setAttribute("data-theme", "dark")
        return ['Light mode', data, "plotly_dark+xiplot_dark"]
    } else {
        document.documentElement.setAttribute("data-theme", "light")
        return ['Dark mode', data, "plotly_white+xiplot_light"]
    }
}
            """,
            Output("light-dark-toggle", "children"),
            Output("light-dark-toggle-store", "data"),
            Output("plotly-template", "data"),
            Input("light-dark-toggle", "n_clicks"),
            State("light-dark-toggle-store", "data"),
            prevent_initial_call=False,
        )

        app.clientside_callback(
            """
            function changeColSize(cols) {
                document.documentElement.setAttribute("data-cols", cols)
                return ' '
            }
            """,
            Output("settings-tab-dummy", "children"),
            Input("settings-column-size", "value"),
            prevent_initial_call=False,
        )

        app.clientside_callback(
            """
            function changePlotHeight(value) {
                document.documentElement.setAttribute("plot-height", value)
                return ' '
            }
            """,
            Output("settings-tab-dummy", "children"),
            Input("settings-plot-height", "value"),
            prevent_initial_call=False,
        )

    @staticmethod
    def create_layout():
        return FlexRow(
            *[
                layout_wrapper(
                    component=html.Button(
                        "Dark mode",
                        id="light-dark-toggle",
                        className="light-dark-toggle button",
                    ),
                    title="Colour scheme",
                ),
                html.Span(" ", id="settings-tab-dummy"),
                layout_wrapper(
                    component=dcc.Dropdown(
                        ["1", "2", "3", "4", "5"],
                        "3",
                        clearable=False,
                        persistence="true",
                        id="settings-column-size",
                    ),
                    title="Maximum number of columns",
                ),
                html.Span(" "),
                layout_wrapper(
                    component=dcc.Slider(
                        min=350,
                        max=650,
                        step=100,
                        marks={i: f"{i}" for i in range(350, 651, 100)},
                        value=450,
                        id="settings-plot-height",
                        persistence="true",
                    ),
                    style={"width": "12rem"},
                    title="Plot height",
                ),
            ]
            + (
                []
                if is_dynamic_plugin_loading_supported()
                else [
                    html.Span(" "),
                    layout_wrapper(
                        component=FlexRow(
                            dcc.Dropdown(
                                get_installed_plugin_options(),
                                id="installed_plugins",
                                clearable=False,
                                searchable=False,
                                placeholder=(
                                    "Check the list of installed plugins"
                                ),
                            ),
                        ),
                        title="Installed Plugins",
                        css_class="dash-dropdown",
                    ),
                ]
            ),
            id="control-settings-container",
            style={"alignItems": "start"},
        )

    @staticmethod
    def create_layout_globals():
        globals = [
            # Store the dark/light state across page reloads
            dcc.Store(
                id="light-dark-toggle-store", data=False, storage_type="local"
            ),
            dcc.Store(id="plotly-template", data=None),
        ]
        return html.Div(globals)


def get_installed_plugin_options():
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
