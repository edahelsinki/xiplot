import pandas as pd

from functools import partialmethod

from dash_extensions.enrich import DashProxy, ServersideOutputTransform, LogTransform

from dashapp.app import DashApp
from dashapp.utils.store import ServerSideStoreBackend

import dash_mantine_components

dash_mantine_components.NotificationsProvider.__init__ = partialmethod(
    dash_mantine_components.NotificationsProvider.__init__, position="top-right"
)

dash_transforms = [LogTransform()]

# FIXME: Only enable on local single-user builds
if True:
    dash_transforms.append(
        ServersideOutputTransform(
            backend=ServerSideStoreBackend(), session_check=False, arg_check=False
        )
    )

    def df_from_store(df):
        return df

    def df_to_store(df):
        return df

else:

    def df_from_store(df):
        return pd.read_json(df, orient="split")

    def df_to_store(df):
        return df.to_json(date_format="iso", orient="split")


dash = DashProxy(
    __name__, suppress_callback_exceptions=True, transforms=dash_transforms
)

app = DashApp(app=dash, df_from_store=df_from_store, df_to_store=df_to_store)
dash.run_server(debug=True)
