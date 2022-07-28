import dash_mantine_components as dmc

from dash import html, dcc

from dashapp.tabs.data import Data
from dashapp.tabs.plots import Plots
from dashapp.tabs.cluster import Cluster


class DashApp:
    def __init__(self, app, df_from_store, df_to_store) -> None:
        self.app = app

        try:
            import dash_uploader as du

            du.configure_upload(app=self.app, folder="uploads", use_upload_id=False)
        except ImportError:
            pass

        TABS = [Data, Plots, Cluster]

        self.app.layout = dmc.NotificationsProvider(
            html.Div(
                [
                    html.Div(
                        [
                            app_logo(),
                            dcc.Tabs(
                                [
                                    dcc.Tab(
                                        [t.create_layout()],
                                        label=t.name(),
                                        value=f"control-{t.name().lower()}-tab",
                                    )
                                    for t in TABS
                                ],
                                id="control-tabs",
                                value=f"control-{TABS[0].name().lower()}-tab",
                            ),
                        ],
                        style={
                            "width": "100%",
                            "display": "inline-block",
                            "background-color": "#dffcde",
                            "height": "auto",
                            "border-radius": "8px",
                        },
                    ),
                    html.Div(id="graphs"),
                    dcc.Store(id="data_frame_store"),
                    dcc.Store(id="clusters_column_store"),
                    dcc.Store(id="selected_rows_store"),
                    html.Div(
                        [t.create_layout_globals() for t in TABS],
                        id="globals",
                    ),
                ],
                id="main",
            ),
            position="top-right",
        )

        for tab in TABS:
            tab.register_callbacks(app, df_from_store, df_to_store)


def app_logo():
    return html.Div(
        [html.H1("Dash App 2022")], style={"text-align": "center", "margin": 20}
    )
