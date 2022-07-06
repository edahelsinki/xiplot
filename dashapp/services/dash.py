from dash import html, dcc

from dashapp.services.data_frame import read_data_file, get_data_files
from dashapp.services.graphs import *
from dashapp.services import dash_layouts
from dashapp.ui.dash_callbacks import Callbacks


class DashApp:
    def __init__(self, app) -> None:
        self.app = app

        try:
            import dash_uploader as du

            du.configure_upload(app=self.app, folder="uploads", use_upload_id=False)
        except ImportError:
            pass

        PLOT_TYPES = {
            "Scatterplot": Scatterplot,
            "Histogram": Histogram,
            "Heatmap": Heatmap,
            "Barplot": Barplot,
        }

        self.app.layout = html.Div(
            [
                dash_layouts.control(PLOT_TYPES),
                dcc.Store(id="data_file_store"),
                dcc.Store(id="data_frame_store"),
                dcc.Store(id="clusters_column_store"),
                dcc.Store(id="uploaded_data_file_store"),
            ],
            id="main",
        )

        self.cb = Callbacks(PLOT_TYPES)
        self.cb.init_callbacks(self.app)

        for plot_type, plot in PLOT_TYPES.items():
            plot.init_callback(app)
