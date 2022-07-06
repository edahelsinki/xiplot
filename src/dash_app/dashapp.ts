//@ts-ignore
window.dashApp = `
import dashapp

from dash import Dash

from dashapp.services.dash import DashApp

app = Dash(__name__, suppress_callback_exceptions=True, compress=False, eager_loading=True)
app = DashApp(app=app).app
`;
