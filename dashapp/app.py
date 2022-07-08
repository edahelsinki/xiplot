from dash import html, dcc

from dashapp.tabs.data import DataTab
from dashapp.tabs.plots import PlotsTab
from dashapp.tabs.cluster import ClusterTab


class DashApp:
    def __init__(self, app, df_from_store, df_to_store) -> None:
        self.app = app

        try:
            import dash_uploader as du

            du.configure_upload(app=self.app, folder="uploads", use_upload_id=False)
        except ImportError:
            pass

        TABS = [DataTab, PlotsTab, ClusterTab]

        self.app.layout = html.Div(
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
                dcc.Store(id="data_frame_store"),
                dcc.Store(id="clusters_column_store"),
                dcc.Store(id="uploaded_data_file_store"),
            ],
            id="main",
        )

        for tab in TABS:
            tab.register_callbacks(app, df_from_store, df_to_store)


def app_logo():
    return html.Div(
        [html.H1("Dash App 2022")], style={"text-align": "center", "margin": 20}
    )
