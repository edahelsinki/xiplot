"""
    This module exposes the parts of xiplot that are useful for implementing plugins.
    Most of the members of this module are just imported from other places in xiplot.
    But there are also some plugin-specific functions and objects.
"""

from typing import Any, Callable, List, Literal, Tuple, Union
from importlib_metadata import entry_points as _entry_points
from io import BytesIO
from os import PathLike

import pandas as pd

# Export useful parts of xiplot:
from xiplot.plots import APlot
from xiplot.utils.components import FlexRow, DeleteButton, PdfButton


# IDs for important `dcc.Store` components:
STORE_DATAFRAME_ID = "data_frame_store"
STORE_METADATA_ID = "metadata_store"
STORE_HOVERED_ID = "lastly_hovered_point_store"
STORE_CLICKED_ID = "lastly_clicked_point_store"
STORE_SELECTED_ID = "selected_rows_store"


# Helpful typehints:
AReadFunction = Callable[[Union[BytesIO, PathLike]], pd.DataFrame]
AReadPlugin = Callable[[], Tuple[AReadFunction, str]]  # str==file extension


# Helper functions:
def get_plugins_cached(plugin_type: Literal["read", "plot"]) -> List[Any]:
    """Get a list of all plugins of the specified type (this call is cached for future reuse).

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

    plugins = [plugin.load() for plugin in plugins]
    get_plugins_cached.cache[plugin_type] = plugins
    return plugins
