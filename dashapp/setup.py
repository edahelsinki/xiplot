import pandas as pd
import dash_extensions.enrich as enrich

from dash_extensions.enrich import (
    DashProxy,
    ServersideOutputTransform,
    MultiplexerTransform,
    CycleBreakerTransform,
)

from dashapp.app import DashApp
from dashapp.utils.store import ServerSideStoreBackend


def setup_dash_app(unsafe_local_server=False, **kwargs):
    dash_transforms = [
        MultiplexerTransform(),
        CycleBreakerTransform(),
    ]

    if unsafe_local_server:
        dash_transforms.append(
            ServersideOutputTransform(
                backend=ServerSideStoreBackend(), session_check=False, arg_check=False
            )
        )

        def df_from_store(df):
            return df.copy(deep=False)

        def df_to_store(df):
            return df

    else:

        def df_from_store(df):
            return pd.read_json(df, orient="split")

        def df_to_store(df):
            return df.to_json(date_format="iso", orient="split")

    dash = DashProxy(
        "dashapp.app",
        suppress_callback_exceptions=True,
        transforms=dash_transforms,
        prevent_initial_callbacks=True,
        **kwargs,
    )

    app = DashApp(app=dash, df_from_store=df_from_store, df_to_store=df_to_store)

    return dash


""" Monkey patch for dash_extensions to remove print """


# https://github.com/thedirtyfew/dash-extensions/commit/d843b63
def _new_get_cache_id(func, output, args, session_check=None, arg_check=True):
    all_args = [func.__name__, enrich._create_callback_id(output)]
    if arg_check:
        all_args += list(args)
    if session_check:
        all_args += [enrich._get_session_id()]
    return enrich.hashlib.md5(enrich.json.dumps(all_args).encode()).hexdigest()


enrich._get_cache_id = _new_get_cache_id
