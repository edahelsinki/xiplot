from xiplot.tabs import Tab
from xiplot.utils.components import FlexRow
from xiplot.utils.layouts import layout_wrapper

from dash import html, Input, Output, dcc


class Settings(Tab):
    def register_callbacks(app, df_from_store, df_to_store):
        app.clientside_callback(
            """
            function toggleLightDarkMode(nClicks) {
                if (nClicks % 2 == 1) {
                    document.documentElement.setAttribute("data-theme", "dark")
                    return 'Light'
                }
                document.documentElement.setAttribute("data-theme", "light")
                return 'Dark'
            }
            """,
            Output("light-dark-toggle", "children"),
            Input("light-dark-toggle", "n_clicks"),
        )
        app.clientside_callback(
            """
            function changeColSize(cols) {
                document.documentElement.setAttribute("data-cols", cols)
                return cols
            }
            """,
            Output("settings-column-size", "value"),
            Input("settings-column-size", "value"),
        )

    def create_layout():
        return FlexRow(
            layout_wrapper(
                component=html.Button(
                    "Dark",
                    id="light-dark-toggle",
                    className="light-dark-toggle button",
                ),
                title="Light/Dark mode",
            ),
            " ",
            layout_wrapper(
                component=dcc.Dropdown(
                    ["1", "2", "3", "4", "5"],
                    "3",
                    clearable=False,
                    id="settings-column-size",
                ),
                title="Maximum number of columns",
            ),
            id="control-settings-container",
        )
