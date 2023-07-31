"""
    This module exposes the parts of xiplot that are useful for implementing plugins.
    Most of the members of this module are just imported from other places in xiplot.
"""

from io import BytesIO
from os import PathLike
from typing import Any, Callable, Dict, Optional, Tuple, Union

import pandas as pd
from dash import Dash
from dash.development.base_component import Component

# Export useful parts of xiplot:
from xiplot.plots import APlot  # noqa: F401
from xiplot.utils import generate_id  # noqa: F401
from xiplot.utils.auxiliary import (  # noqa: F401
    decode_aux,
    encode_aux,
    get_clusters,
    get_selected,
    merge_df_aux,
)
from xiplot.utils.cluster import cluster_colours  # noqa: F401
from xiplot.utils.components import (  # noqa: F401
    ClusterDropdown,
    ColumnDropdown,
    DeleteButton,
    FlexRow,
    HelpButton,
    PdfButton,
    PlotData,
)

# IDs for important `dcc.Store` components:
ID_DATAFRAME = "data_frame_store"  # Main dataframe (readonly)
ID_AUXILIARY = "auxiliary_store"  # Additional dataframe (editable)
ID_METADATA = "metadata_store"
ID_HOVERED = "lastly_hovered_point_store"
ID_CLICKED = "lastly_clicked_point_store"
# `dcc.Store` that is `True` if the dark mode is active
ID_DARK_MODE = "light-dark-toggle-store"
# `dcc.Store` that contains the current plotly template (used for the dark mode)
ID_PLOTLY_TEMPLATE = "plotly-template"

# Useful CSS classes
CSS_STRETCH_CLASS = "stretch"
CSS_LARGE_BUTTON_CLASS = "button"
CSS_DELETE_BUTTON_CLASS = "delete"


# Helpful typehints:
AReadFunction = Callable[[Union[BytesIO, PathLike]], pd.DataFrame]
# Read plugin return string: file extension
AReadPlugin = Callable[[], Optional[Tuple[AReadFunction, str]]]
AWriteFunction = Callable[[pd.DataFrame, BytesIO], None]
# Write plugin return strings: file extension, MIME type
#  (ususally "application/octet-stream")
AWritePlugin = Callable[[], Optional[Tuple[AWriteFunction, str, str]]]
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
