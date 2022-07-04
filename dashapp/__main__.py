from dash import Dash

from dashapp.services.dash import DashApp

dash = Dash(__name__, suppress_callback_exceptions=True)
app = DashApp(app=dash)
dash.run_server(debug=True)
