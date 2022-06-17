from dash import html, dcc
from services.main_dash import app
from services.data_frame import read_data_file, get_data_files
import services.dash_layouts as dash_layouts
from ui.dash_callbacks import Callbacks


class DashApp:
    def __init__(self) -> None:
        pass

    def start(self):
        app.layout = html.Div([
            dash_layouts.app_logo(),
            dash_layouts.scatterplot(),
            dash_layouts.histogram(),
            dash_layouts.control(),
            dash_layouts.selected_histogram(),
            dash_layouts.smiles()
        ])

        cb = Callbacks()
        cb.get_callbacks(app)

        app.run_server()
