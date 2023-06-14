from collections import Counter

import dash_mantine_components as dmc
from dash import ALL, Input, Output, ctx, dcc, html

from xiplot.plugin import (
    get_plugins_cached,
    is_dynamic_plugin_loading_supported,
)
from xiplot.tabs.cluster import Cluster, get_clusters
from xiplot.tabs.data import Data
from xiplot.tabs.embedding import Embedding
from xiplot.tabs.plots import Plots
from xiplot.tabs.plugins import Plugins
from xiplot.tabs.settings import Settings
from xiplot.utils.components import PdfButton


class XiPlot:
    def __init__(
        self, app, df_from_store, df_to_store, data_dir="", plugin_dir=""
    ) -> None:
        self.app = app
        self.app.title = "χiplot"

        try:
            import dash_uploader as du

            du.configure_upload(
                app=self.app, folder="uploads", use_upload_id=False
            )
        except (ImportError, AttributeError):
            pass

        TABS = [Data, Plots, Cluster, Embedding, Settings]

        if is_dynamic_plugin_loading_supported():
            TABS.insert(-1, Plugins)

        self.app.layout = dmc.NotificationsProvider(
            html.Div(
                [
                    html.Div(
                        [
                            app_logo(),
                            dcc.Tabs(
                                [
                                    dcc.Tab(
                                        [
                                            (
                                                t.create_layout(
                                                    data_dir=data_dir
                                                )
                                                if t == Data
                                                else (
                                                    t.create_layout(
                                                        plugin_dir=plugin_dir
                                                    )
                                                    if t == Plugins
                                                    else t.create_layout()
                                                )
                                            )
                                        ],
                                        label=t.name(),
                                        value=(
                                            f"control-{t.name().lower()}-tab"
                                        ),
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
                    dcc.Store(id="auxiliary_store"),
                    dcc.Store(id="metadata_store"),
                    dcc.Store(id="selected_rows_store"),
                    dcc.Store(id="lastly_clicked_point_store"),
                    dcc.Store(id="lastly_hovered_point_store"),
                    html.Div(
                        [t.create_layout_globals() for t in TABS],
                        id="globals",
                    ),
                    PdfButton.create_global(),
                    html.Div(
                        [g() for (_, _, g) in get_plugins_cached("global")],
                        id="plugin-globals",
                    ),
                ],
                id="main",
            ),
            position="top-right",
        )

        for tab in TABS:
            (
                tab.register_callbacks(
                    app, df_from_store, df_to_store, data_dir=data_dir
                )
                if tab == Data
                else (
                    tab.register_callbacks(
                        app,
                        df_from_store,
                        df_to_store,
                        plugin_dir=plugin_dir,
                    )
                    if tab == Plugins
                    else tab.register_callbacks(
                        app, df_from_store, df_to_store
                    )
                )
            )

        for _, _, cb in get_plugins_cached("callback"):
            cb(app, df_from_store, df_to_store)

        @app.callback(
            Output(
                {"type": "cluster-dropdown-count", "index": ALL}, "children"
            ),
            Input("auxiliary_store", "data"),
            prevent_initial_call=False,
        )
        def cluster_dropdown_count_callback(aux):
            if aux is None:
                clusters = []
            else:
                clusters = get_clusters(df_from_store(aux))
            counter = Counter(clusters)

            counts = []

            for output in ctx.outputs_list:
                cluster = output["id"]["index"].split("-")[0]

                if cluster == "all":
                    if len(clusters) == 0:
                        counts.append("all")
                    else:
                        counts.append(len(clusters))
                else:
                    counts.append(counter[cluster])

            return [f": [{c}]" for c in counts]


def app_logo():
    return html.Div([html.H1("χiplot")], id="logo", className="logo")
