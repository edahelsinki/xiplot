from abc import ABC, abstractclassmethod
from typing import Any, Callable, List, Optional, Dict

import pandas as pd
from dash import Dash, html, dcc

from xiplot.utils import generate_id
from xiplot.utils.components import DeleteButton, PdfButton


class APlot(ABC):
    """Abstract class that defines the API for implementing a new plot"""

    def __init__(self):
        raise TypeError("APlot should not be constructed")

    @classmethod
    def name(cls) -> str:
        """The name that is shown in the UI when selecting plots."""
        return cls.__name__

    @classmethod
    def get_id(cls, index: Any, subtype: Optional[str] = None) -> Dict[str, Any]:
        """Generate id:s for the plot.

        Args:
            index: Index of the plot.
            subtype: Differentiatie parts of the plot. Defaults to None.

        Returns:
            Dash id.
        """
        return generate_id(cls, index, subtype)

    @abstractclassmethod
    def register_callbacks(
        cls,
        app: Dash,
        df_from_store: Callable[[Any], pd.DataFrame],
        df_to_store: Callable[[pd.DataFrame], Any],
    ):
        """Override this to register Dash callbacks for your plot.

        Args:
            app: The xiplot app (a subclass of `dash.Dash`).
            df_from_store: Functions that transforms `dcc.Store` data into a dataframe.
            df_to_store: Function that transform a dataframe into `dcc.Store` data.
        """
        pass

    @abstractclassmethod
    def create_new_layout(
        cls, index: Any, df: pd.DataFrame, columns: Any, config: Dict[str, Any] = dict()
    ) -> html.Div:
        """Overide this method to create a layout for your plot.
        Alternatively you can overload `APlot.create_layout` for a simplified setup.

        Args:
            index: The index of the plot.
            df: Dataframe.
            columns: TODO
            config: TODO. Defaults to dict().

        Returns:
            A html element presenting the plot.
        """
        children = cls.create_layout(index, df, columns, config)
        if any(isinstance(e, dcc.Graph) for e in children):
            children = [DeleteButton(index), PdfButton(index)] + children
        else:
            children = [DeleteButton(index)] + children
        return html.Div(children, id=cls.get_id(index, "panel"), className="plots")

    @abstractclassmethod
    def create_layout(
        cls, index: Any, df: pd.DataFrame, columns: Any, config: Dict[str, Any]
    ) -> List[Any]:
        """If `APlot.create_new_layout` is not overriden, then this method can be overriden to provide a "Standard" plot.

        A "standard" plot has the following features:
            - The children (given by this function) are wrapped in a Div with `className="plots"`.
            - A delete button is added.
            - A "Download pdf" button is added if any of the children is a `dcc.Graph`.

        Args:
            index: The index of the plot
            df: Dataframe.
            columns: TODO
            config: TODO

        Returns:
            A list of (child) html components.
        """
        return ["Not implemented"]
