"""
    This module exposes the parts of xiplot that are useful for implementing
    plugins. Most of the members of this module are just imported from other
    places in xiplot. But there are also some plugin-specific functions and
    objects.
"""

from collections import defaultdict
from importlib.metadata import entry_points as _entry_points
from io import BytesIO
from os import PathLike
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
) -> List[Tuple[str, str, Any]]:
    """Get a list of all plugins of the specified type
     (this call is cached for future reuse).

    Args:
        plugin_type: The type of xiplot plugin.

    Returns:
        A list of tuples of each plugin's name, path, and its
        loaded `entry_point`.
    """
    if getattr(get_plugins_cached, "cache", None) is None:
        get_plugins_cached.cache = dict()

    cached_plugins_of_type = get_plugins_cached.cache.get(plugin_type, None)

    if cached_plugins_of_type is not None:
        return cached_plugins_of_type

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


def get_new_plugins_cached(
    plugin_type: Literal["read", "write", "plot", "global", "callback"]
) -> List[Tuple[str, str, Any]]:
    """Get a list of all new plugins of the specified type that have been
     added since the last call of this function (this call is cached for
     future reuse).

    Args:
        plugin_type: The type of xiplot plugin.

    Returns:
        A list of tuples of each plugin's name, path, and its
        loaded `entry_point`.
    """
    if getattr(get_new_plugins_cached, "cache", None) is None:
        get_new_plugins_cached.cache = defaultdict(list)

    current_plugins = get_plugins_cached(plugin_type)

    new_plugins = []

    for name, path, plugin in current_plugins:
        new = True

        for old_name, old_path, old_plugin in get_new_plugins_cached.cache[
            plugin_type
        ]:
            if path == old_path:
                new = False
                break

        if new:
            new_plugins.append((name, path, plugin))

    get_new_plugins_cached.cache[plugin_type] += new_plugins

    return new_plugins


def get_all_loaded_plugins() -> List[Tuple[str, str, str, Any]]:
    """Collects the list of all loaded plugins and their types.

    Returns:
        A list of tuples of each plugin's type, name, path, and its
        loaded `entry_point`.

    """
    plugins = []

    for plugin_type in ["read", "write", "plot", "global", "callback"]:
        for name, path, plugin in get_plugins_cached(plugin_type):
            plugins.append((plugin_type, name, path, plugin))

    return plugins


def is_dynamic_plugin_loading_supported() -> bool:
    """Checks if xiplot supports dynamically loading new plugins at runtime.

    Returns:
        `True` if dynamic loading is supported, `False` otherwise.
    """
    try:
        import micropip  # noqa: F401
    except ImportError:
        return False

    return True
