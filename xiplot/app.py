import dash_mantine_components as dmc

from collections import Counter

from dash import html, dcc, Input, Output, ALL, ctx
from xiplot.plugin import get_plugins_cached

from xiplot.tabs.data import Data
from xiplot.tabs.plots import Plots
from xiplot.tabs.cluster import Cluster
from xiplot.tabs.settings import Settings
from xiplot.tabs.embedding import Embedding

from xiplot.utils.cluster import cluster_colours
from xiplot.utils.components import PdfButton


class XiPlot:
    def __init__(self, app, df_from_store, df_to_store) -> None:
        self.app = app
        self.app.title = "χiplot"

        try:
            import dash_uploader as du

            du.configure_upload(app=self.app, folder="uploads", use_upload_id=False)
        except (ImportError, AttributeError):
            pass

        TABS = [Data, Plots, Cluster, Embedding, Settings]

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
                        id="control",
                        className="control",
                    ),
                    html.Div(id="plots"),
                    dcc.Store(id="data_frame_store"),
                    dcc.Store(id="metadata_store"),
                    dcc.Store(id="clusters_column_store"),
                    dcc.Store(id="pca_column_store"),
                    html.Div(
                        id="clusters_column_store_reset", style={"display": "none"}
                    ),
                    dcc.Store(id="selected_rows_store"),
                    dcc.Store(id="lastly_clicked_point_store"),
                    dcc.Store(id="lastly_hovered_point_store"),
                    html.Div(
                        [t.create_layout_globals() for t in TABS],
                        id="globals",
                    ),
                    PdfButton.create_global(),
                ]
                + [g() for g in get_plugins_cached("global")],
                id="main",
            ),
            position="top-right",
        )

        for tab in TABS:
            tab.register_callbacks(app, df_from_store, df_to_store)

        for cb in get_plugins_cached("callback"):
            cb(app, df_from_store, df_to_store)

        @app.callback(
            Output({"type": "cluster-dropdown-count", "index": ALL}, "children"),
            Input("clusters_column_store", "data"),
            prevent_initial_call=False,
        )
        def cluster_dropdown_count_callback(kmeans_store):
            if kmeans_store is None:
                kmeans_store = []

            counter = Counter(kmeans_store)

            counts = []

            for output in ctx.outputs_list:
                cluster = output["id"]["index"].split("-")[0]

                if cluster == "all":
                    counts.append(len(kmeans_store))
                else:
                    counts.append(counter[cluster])

            return [f": [{c}]" for c in counts]


def app_logo():
    return html.Div([html.H1("χiplot")], id="logo", className="logo")
