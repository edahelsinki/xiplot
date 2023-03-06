from xiplot.tabs import Tab
from xiplot.utils.components import FlexRow
from xiplot.utils.layouts import layout_wrapper

from dash import html, Input, Output, dcc, State, Dash


class Settings(Tab):
    @staticmethod
    def register_callbacks(app: Dash, df_from_store, df_to_store):
        app.clientside_callback(
            """
            function toggleLightDarkMode(clicks, data) {
                if (clicks != undefined) {
                    data = !data
                }
                if (data) {
                    document.documentElement.setAttribute("data-theme", "dark")
                    return ['Light mode', data]
                } else {
                    document.documentElement.setAttribute("data-theme", "light")
                    return ['Dark mode', data]
                }
            }
            """,
            Output("light-dark-toggle", "children"),
            Output("light-dark-toggle-store", "data"),
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

    @staticmethod
    def create_layout():
        return FlexRow(
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
                    persistence="True",
                    id="settings-column-size",
                ),
                title="Maximum number of columns",
            ),
            id="control-settings-container",
        )

    @staticmethod
    def create_layout_globals():
        # Store the dark/light state across page reloads
        return dcc.Store(id="light-dark-toggle-store", data=False, storage_type="local")
