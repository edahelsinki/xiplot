from abc import ABC, abstractclassmethod
from typing import Any, Callable, List, Optional, Dict

import pandas as pd
from dash import Dash, html, dcc

from xiplot.utils import generate_id
from xiplot.utils.components import DeleteButton, FlexRow, PdfButton, PlotData


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

        You might also want to call `PlotData.register_callback` and `PdfButton.register_callback` here.

        Args:
            app: The xiplot app (a subclass of `dash.Dash`).
            df_from_store: Functions that transforms `dcc.Store` data into a dataframe.
            df_to_store: Function that transform a dataframe into `dcc.Store` data.
        """
        # If a PdfButton is added to the layout, remember to do:
        # PdfButton.register_callback(app, cls.get_id(None))
        # If a PlotData is added to the layout (to enable saving of the plot), remember to do:
        # PlotData.register_callback(app, cls.name(), ...)
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
            columns: Columns from the dataframe to use in the plot.
            config: Plot configuration (used when restoring saved plots). Defaults to dict().

        Returns:
            A html element presenting the plot.
        """
        children = cls.create_layout(index, df, columns, config)
        buttons = DeleteButton(index)
        if any(isinstance(e, dcc.Graph) for e in children):
            buttons = FlexRow(buttons, html.Div(className="stretch"), PdfButton(index))
        children.insert(0, buttons)
        children.append(PlotData(index, cls.name()))
        return html.Div(children, id=cls.get_id(index, "panel"), className="plots")

    @abstractclassmethod
    def create_layout(
        cls, index: Any, df: pd.DataFrame, columns: Any, config: Dict[str, Any] = dict()
    ) -> List[Any]:
        """If `APlot.create_new_layout` is not overriden, then this method can be overriden to provide a "standard" plot.

        A "standard" plot has the following features:
            - The children (given by this function) are wrapped in a Div with `className="plots"`.
            - A `DeleteButton` is added, so that the plot can be removed.
            - A `PdfButton` is added if any of the children is a `dcc.Graph`.
            - A `PlotData` is added, so that the plot can be saved.

        Args:
            index: The index of the plot
            df: Dataframe.
            columns: Columns from the dataframe to use in the plot.
            config: Plot configuration (used when restoring saved plots). Defaults to dict().

        Returns:
            A list of (child) html components.
        """
        return ["Not implemented"]
