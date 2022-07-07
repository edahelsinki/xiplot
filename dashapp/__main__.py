from dash_extensions.enrich import DashProxy, ServersideOutputTransform

from dashapp.services.dash import DashApp
from dashapp.services.store import ServerSideStoreBackend

dash_transforms = []

# FIXME: Only enable on local single-user builds
if True:
    dash_transforms.append(
        ServersideOutputTransform(
            backend=ServerSideStoreBackend(), session_check=False, arg_check=False
        )
    )

dash = DashProxy(
    __name__, suppress_callback_exceptions=True, transforms=dash_transforms
)
dash._favicon = "favicon.ico"

app = DashApp(app=dash)
dash.run_server(debug=True)
