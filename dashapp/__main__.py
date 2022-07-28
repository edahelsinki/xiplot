import pandas as pd

import dash_extensions.enrich

# FIXME: Monkey patch for dash_extensions until
#        https://github.com/thedirtyfew/dash-extensions/commit/d843b63


def _new_get_cache_id(func, output, args, session_check=None, arg_check=True):
    all_args = [func.__name__, dash_extensions.enrich._create_callback_id(output)]
    if arg_check:
        all_args += list(args)
    if session_check:
        all_args += [dash_extensions.enrich._get_session_id()]
    return dash_extensions.enrich.hashlib.md5(
        dash_extensions.enrich.json.dumps(all_args).encode()
    ).hexdigest()


dash_extensions.enrich._get_cache_id = _new_get_cache_id

from dash_extensions.enrich import DashProxy, ServersideOutputTransform

from dashapp.app import DashApp
from dashapp.utils.store import ServerSideStoreBackend

dash_transforms = []

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
    __name__,
    suppress_callback_exceptions=True,
    transforms=dash_transforms,
    prevent_initial_callbacks=True,
)

app = DashApp(app=dash, df_from_store=df_from_store, df_to_store=df_to_store)
dash.run_server(debug=True)
