from xiplot.tabs import Tab
from xiplot.utils.layouts import layout_wrapper

from dash import html, Input, Output


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

    def create_layout():
        return html.Div(
            [
                layout_wrapper(
                    component=html.Button(
                        "Dark",
                        id="light-dark-toggle",
                        className="light-dark-toggle",
                    ),
                    title="Light/Dark mode",
                )
            ],
            id="control-settings-container",
        )
