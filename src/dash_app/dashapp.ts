//@ts-ignore
window.dashApp = `
import dashapp

from dash import Dash

from dashapp.services.dash import DashApp

dash = Dash(__name__, suppress_callback_exceptions=True, compress=False)
app = DashApp(app=dash).app
`;
