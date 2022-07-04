from dash import html, dcc

from dashapp.services.data_frame import read_data_file, get_data_files
from dashapp.services import dash_layouts
from dashapp.ui.dash_callbacks import Callbacks


class DashApp:
    def __init__(self, app) -> None:
        self.app = app

        try:
            import dash_uploader as du

            du.configure_upload(app=self.app, folder="data", use_upload_id=True)
        except ImportError:
            pass

        self.app.layout = html.Div(
            [
                dash_layouts.control(),
                dash_layouts.scatterplot(),
                dash_layouts.histogram(),
                dcc.Store(id="data_file_store"),
                dcc.Store(id="data_frame_store"),
                dcc.Store(id="clusters_column_store"),
                dcc.Store(id="uploaded_data_file_store"),
            ]
        )

        self.cb = Callbacks()
        self.cb.init_callbacks(self.app)
