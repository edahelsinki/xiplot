"""
    This module exposes the parts of xiplot that are useful for implementing
    plugins. Most of the members of this module are just imported from other
    places in xiplot. But there are also some plugin-specific functions and
    objects.
"""

import uuid
from asyncio import Future
from importlib.metadata import entry_points as _entry_points
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Tuple, Union
from warnings import warn

import pandas as pd
from dash import Dash
from dash.development.base_component import Component

# Export useful parts of xiplot:
from xiplot.plots import APlot  # noqa: F401
from xiplot.utils import generate_id  # noqa: F401
from xiplot.utils.components import (  # noqa: F401
    DeleteButton,
    FlexRow,
    HelpButton,
    PdfButton,
    PlotData,
)

# IDs for important `dcc.Store` components:
ID_DATAFRAME = STORE_DATAFRAME_ID = "data_frame_store"
ID_METADATA = STORE_METADATA_ID = "metadata_store"
ID_HOVERED = STORE_HOVERED_ID = "lastly_hovered_point_store"
ID_CLICKED = STORE_CLICKED_ID = "lastly_clicked_point_store"
ID_SELECTED = STORE_SELECTED_ID = "selected_rows_store"
# `dcc.Store` that is `True` if the dark mode is active
ID_DARK_MODE = "light-dark-toggle-store"
# `dcc.Store` that contains the current plotly template
#  (used for the dark mode)
ID_PLOTLY_TEMPLATE = "plotly-template"

# Useful CSS classes
CSS_STRETCH_CLASS = "stretch"
CSS_LARGE_BUTTON_CLASS = "button"
CSS_DELETE_BUTTON_CLASS = "delete"


# Helpful typehints:
AReadFunction = Callable[[Union[BytesIO, PathLike]], pd.DataFrame]
# Read plugin return string: file extension
AReadPlugin = Callable[[], Tuple[AReadFunction, str]]
AWriteFunction = Callable[[pd.DataFrame, BytesIO], None]
# Write plugin return strings: file extension, MIME type
#  (ususally "application/octet-stream")
AWritePlugin = Callable[[], Tuple[AWriteFunction, str, str]]
AGlobalPlugin = Callable[[], Component]
# Callback plugin functions: parse_to_dataframe, serialise_from_dataframe
ACallbackPlugin = Callable[
    [Dash, Callable[[Any], pd.DataFrame], Callable[[pd.DataFrame], Any]], None
]


# Helper functions:
def placeholder_figure(text: str) -> Dict[str, Any]:
    """Display a placeholder text instead of a graph.
    This can be used in a "callback" function when a graph cannot be rendered.

    Args:
        text: Placeholder text.

    Returns:
        Dash figure (to place into a `Output(dcc.Graph.id, "figure")`).
    """
    return {
        "layout": {
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "annotations": [
                {
                    "text": text,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 28},
                }
            ],
        }
    }


def get_plugins_cached(
    plugin_type: Literal["read", "write", "plot", "global", "callback"]
) -> List[Any]:
    """Get a list of all plugins of the specified type
     (this call is cached for future reuse).

    Args:
        plugin_type: The type of xiplot plugin.

    Returns:
        A list of loaded `entry_points`.
    """
    try:
        if plugin_type in get_plugins_cached.cache:
            return get_plugins_cached.cache[plugin_type]
    except AttributeError:
        get_plugins_cached.cache = dict()

    try:
        # Python 3.10+
        plugins = _entry_points(group=f"xiplot.plugin.{plugin_type}")
    except TypeError:
        # Python 3.8-3.9
        plugins = _entry_points().get(f"xiplot.plugin.{plugin_type}", ())

    loaded_plugins = []
    for plugin in plugins:
        try:
            loaded_plugins.append((plugin.name, plugin.value, plugin.load()))
        except Exception as e:
            warn(f"Could not load plugin {plugin}: {e}")

    get_plugins_cached.cache[plugin_type] = loaded_plugins
    return loaded_plugins


def get_plugin_filepaths(dir_path=""):
    try:
        return sorted(
            (
                fp
                for fp in Path(dir_path).iterdir()
                if fp.is_file() and fp.suffix == ".whl"
            ),
            reverse=True,
        )

    except FileNotFoundError:
        return []


def __micropip_install_callback(future: Future):
    get_plugins_cached.cache = dict()

    try:
        future.result()
        print(
            "pyodide-eval:let plugin_tab_load_success ="
            ' window.document.getElementById("plugin-tab-load-success");let'
            " nativeInputValueSetter = window.Object.getOwnPropertyDescriptor"
            "(window.HTMLInputElement.prototype,"
            ' "value").set;nativeInputValueSetter.call('
            f"plugin_tab_load_success, {repr(str(uuid.uuid4()))});let"
            ' plugin_tab_load_success_event = new Event("input", {'
            " bubbles: true }"
            " );plugin_tab_load_success.dispatchEvent("
            "plugin_tab_load_success_event);"
        )
    except Exception as err:
        print(
            "pyodide-eval:let plugin_tab_load_exception ="
            ' window.document.getElementById("plugin-tab-load-exception");let'
            " nativeInputValueSetter = window.Object.getOwnPropertyDescriptor"
            "(window.HTMLInputElement.prototype,"
            ' "value").set;nativeInputValueSetter.call('
            f"plugin_tab_load_exception, {repr(str(err))});let "
            "plugin_tab_load_exception_event = new"
            ' Event("input", { bubbles: true }'
            " );plugin_tab_load_exception.dispatchEvent("
            "plugin_tab_load_exception_event);"
        )


def install_local_plugin(plugin_path: str):
    import asyncio

    try:
        import micropip
    except ImportError:
        raise NotImplementedError(
            "Loading new plugins is only supported in WASM"
        )

    plugin_path = str(Path(plugin_path).resolve())

    asyncio.ensure_future(
        micropip.install(f"emfs:{plugin_path}")
    ).add_done_callback(__micropip_install_callback)


def install_remote_plugin(plugin_source: str):
    import asyncio

    try:
        import micropip
    except ImportError:
        raise NotImplementedError(
            "Loading new plugins is only supported in WASM"
        )

    if len(plugin_source.split()) != 1:
        raise ValueError("Plugin source must be a URL or PyPi package name")

    if (
        Path(plugin_source).exists()
        and Path(plugin_source).name != plugin_source
    ):
        raise ValueError("Plugin source must be a URL or PyPi package name")

    asyncio.ensure_future(micropip.install(plugin_source)).add_done_callback(
        __micropip_install_callback
    )


def get_all_loaded_plugins():
    plugins = []

    for plugin_type in ["read", "write", "plot", "global", "callback"]:
        for name, path, _ in get_plugins_cached(plugin_type):
            plugins.append((plugin_type, name, path))

    return plugins


def is_plugin_loading_supported() -> bool:
    try:
        import micropip  # noqa: F401
    except ImportError:
        return False

    return True
