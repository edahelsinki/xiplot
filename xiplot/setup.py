import dash_extensions.enrich as enrich
import pandas as pd
from dash_extensions.enrich import (
    CycleBreakerTransform,
    DashProxy,
    MultiplexerTransform,
    ServersideOutputTransform,
)

from xiplot.app import XiPlot
from xiplot.utils.store import ServerSideStoreBackend


def setup_xiplot_dash_app(
    unsafe_local_server=False, data_dir="", plugin_dir="", **kwargs
):
    dash_transforms = [
        MultiplexerTransform(),
        CycleBreakerTransform(),
    ]

    if unsafe_local_server:
        dash_transforms.append(
            ServersideOutputTransform(
                backend=ServerSideStoreBackend(),
                session_check=False,
                arg_check=False,
            )
        )

        def df_from_store(df):
            if isinstance(df, pd.DataFrame):
                return df.copy(deep=False)
            return df

        def df_to_store(df):
            return df

    else:

        def df_from_store(df):
            return pd.read_json(df, orient="split")

        def df_to_store(df):
            return df.to_json(date_format="iso", orient="split")

    dash = DashProxy(
        "xiplot.app",
        suppress_callback_exceptions=True,
        transforms=dash_transforms,
        prevent_initial_callbacks=True,
        **kwargs,
    )

    _app = XiPlot(  # noqa: F841
        app=dash,
        df_from_store=df_from_store,
        df_to_store=df_to_store,
        data_dir=data_dir,
        plugin_dir=plugin_dir,
    )

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
