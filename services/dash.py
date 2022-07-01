from dash import html, dcc
from services.main_dash import app
from services.data_frame import read_data_file, get_data_files
import services.dash_layouts as dash_layouts
from ui.dash_callbacks import Callbacks


class DashApp:
    def __init__(self) -> None:
        app.layout = html.Div(
            [
                dash_layouts.control(),
                dash_layouts.scatterplot(),
                dash_layouts.histogram(),
                dcc.Store(id="data_frame_store"),
                dcc.Store(id="data_file_store"),
                dcc.Store(id="scatterplot_input_store"),
                dcc.Store(id="clusters_column_store"),
            ]
        )

    def start(self):
        cb = Callbacks()
        cb.get_callbacks(app)

        app.run_server(debug=True)
