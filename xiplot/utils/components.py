import base64
import uuid
from collections import Counter
from io import BytesIO
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

import pandas as pd
import plotly as po
from dash import (
    ALL,
    MATCH,
    Dash,
    Input,
    Output,
    State,
    ctx,
    dcc,
    html,
    no_update,
)

from xiplot.utils import generate_id
from xiplot.utils.auxiliary import decode_aux, get_clusters
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.regex import dropdown_regex


class FlexRow(html.Div):
    """
    Create a Div with a "display: flex" style.
    This makes the children appear on one line (with wrapping if necessary).
    Any child with a `className="stretch"` will fill all the empty space of
    the line. `dcc.Dropdown` automatically stretch with a minimum length
    (see `html_components.css`).

    Example:
        row = FlexRow(
            dcc.Dropown(["A", "B"]),
            html.Button("Accept"),
            id="example",
        )
    """

    def __init__(self, *children, className: Optional[str] = None, **kwargs):
        if className is None:
            className = "flex-row"
        else:
            className = className + " flex-row"
        super().__init__(
            children=list(children), className=className, **kwargs
        )


class InputText(html.Div):
    def __init__(
        self,
        *args,
        className: Optional[str] = None,
        type: str = "text",
        div_kws: Dict[str, Any] = {},
        **kwargs,
    ):
        """Create a `dcc.Input` wrapped in a `html.Div` with `className`s to
        make it match `dcc.Dropdown`.

        Args:
            *args: Arguments forwarded to `dcc.Input`.
            className: Additional classnames for the `html.Div`. Defaults to
                None.
            type: Type of `dcc.Input`. Defaults to "text".
            div_kws: Additional arguments to the `html.Div`. Defaults to {}.
            **kwargs: Keyword arguments forwarded to `dcc.Input`.
        """
        inp = dcc.Input(
            *args, type=type, className="Select-input Select-control", **kwargs
        )
        if className is not None:
            className = "Select " + className
        else:
            className = "Select"
        super().__init__(children=inp, className=className, **div_kws)


class ColumnDropdown(dcc.Dropdown):
    def __init__(
        self,
        id: Dict,
        *args,
        **kwargs,
    ):
        """Create a `dcc.Dropdown` for selecting columns from the data frame
        and auxiliary data frame.

        Args:
            id: Element id.
            *args: Arguments forwarded to `dcc.Dropdown`.
            regex: Add a hidden synced input field for regex matching.
            *kwargs: Keyword arguments forwarded to `dcc.Dropdown`.
        """
        super().__init__(
            *args,
            id=id,
            **kwargs,
        )

    @classmethod
    def get_columns(
        cls,
        df: pd.DataFrame,
        aux: Optional[pd.DataFrame] = None,
        options: List[str] = [],
        numeric: bool = False,
        category: bool = False,
    ) -> List[str]:
        """Get column names from the data frame and auxiliary data frame.

        Args:
            df: Data frame.
            aux: Auxiliary data frame. Defaults to None.
            options: Additional options to add to the column names. Defaults to [].
            numeric: Only select numeric columns. Defaults to False.
            category: Only select categorical (and integer, and object) columns.
              Defaults to False.

        Returns:
            List of column names
        """
        if aux is None:
            aux = pd.DataFrame()
        if numeric:
            return (
                options
                + df.select_dtypes("number").columns.to_list()
                + aux.select_dtypes("number").columns.to_list()
            )
        elif category:
            return (
                options
                + df.select_dtypes(
                    ["number", "category", "object"], "float"
                ).columns.to_list()
                + aux.select_dtypes(
                    ["number", "category", "object"], "float"
                ).columns.to_list()
            )
        else:
            return options + df.columns.to_list() + aux.columns.to_list()

    @classmethod
    def register_callback(
        cls,
        app: Dash,
        id: Dict,
        df_from_store: Callable,
        options: List[str] = [],
        numeric: bool = False,
        category: bool = False,
        regex_button_id: Optional[Dict] = None,
        regex_input_id: Optional[Dict] = None,
    ):
        """Register callbacks for the dropdowns.
        Call this once per unique id (ignoring index).

        Args:
            app: Dash app.
            id: Dropdown id.
            df_from_store: Function for extracting dataframes from store.
            options: See `ColumnDropdown.get_columns()`. Defaults to [].
            numeric: See `ColumnDropdown.get_columns()`. Defaults to False.
            category: See `ColumnDropdown.get_columns()`. Defaults to False.
            regex_button_id: Id for the "add regex" button, if this dropdown
              accepts regex. Defaults to None.
            regex_input_id: Id for a hidden input (that will be synced to the
              dropdown), if this dropdown accepts regex. Defaults to None.
        """
        if regex_button_id is None or regex_input_id is None:
            if isinstance(id, dict) and "index" in id:
                id["index"] = ALL

            @app.callback(
                Output(id, "options"),
                Input("data_frame_store", "data"),
                Input("auxiliary_store", "data"),
                State(id, "value"),
                prevent_initial_call=False,
            )
            def update_columns(df, aux, dds):
                if df is None:
                    return no_update
                df = df_from_store(df)
                aux = decode_aux(aux)
                columns = cls.get_columns(df, aux, options, numeric, category)
                if isinstance(id, dict) and "index" in id:
                    return [columns] * len(dds)
                else:
                    return columns

        else:
            if isinstance(id, dict) and "index" in id:
                id["index"] = MATCH
                regex_button_id["index"] = MATCH
                regex_input_id["index"] = MATCH

            # Sync `dropdown.search_value` and "regex_input"
            app.clientside_callback(
                """
                function (input) {
                if (input == "") {
                    return window.dash_clientside.no_update;
                }
                return input;
                }
                """,
                Output(regex_input_id, "value"),
                Input(id, "search_value"),
            )

            @app.callback(
                Output(id, "options"),
                Output(id, "value"),
                Output(id, "search_value"),
                Input("data_frame_store", "data"),
                Input("auxiliary_store", "data"),
                Input(regex_button_id, "n_clicks"),
                Input(id, "value"),
                State(regex_input_id, "value"),
                prevent_initial_call=False,
            )
            def update_columns_regex(df, aux, _nc, selected, regex):
                if df is None:
                    return no_update, no_update, no_update
                df = df_from_store(df)
                aux = decode_aux(aux)
                columns = cls.get_columns(df, aux, options, numeric, category)

                if ctx.triggered_id == regex_button_id or (
                    isinstance(ctx.triggered_id, dict)
                    and ctx.triggered_id["type"] == regex_button_id["type"]
                ):
                    new_search = ""
                else:
                    regex = None
                    new_search = no_update

                columns, selected, _ = dropdown_regex(columns, selected, regex)
                return columns, selected, new_search


class ClusterDropdown(dcc.Dropdown):
    def __init__(
        self,
        *args,
        index: Optional[str] = None,
        id: Optional[Dict] = None,
        **kwargs,
    ):
        """Create a `dcc.Dropdown` for selecting clusters.

        Args:
            index: Index of the dropdown (to be used with the default id).
              Defaults to None.
            id: Optionally override the default id (see
              `ClusterDropdown.register_callbacks()`). Defaults to None.
        """
        if not id:
            id = self.get_id(index if index is not None else str(uuid.uuid4()))
        super().__init__(*args, id=id, options=self.get_options(), **kwargs)

    @classmethod
    def get_id(cls, index: str):
        return generate_id(cls, index)

    @classmethod
    def get_options(
        cls, clusters: Optional[pd.Categorical] = None, empty: bool = False
    ) -> List[object]:
        """Generate the options for a ClusterDropdown.

        Args:
            clusters: Optional column of cluster ids. Defaults to None.
            empty: Include emtpy clusters. Defaults to False.

        Returns:
            List of Dropdown options.
        """
        cc = cluster_colours()
        if clusters is None:
            counter = {k: "" for k in cc.keys()}
        else:
            counter = {k: f": [{v}]" for k, v in Counter(clusters).items()}
            counter["all"] = f": [{len(clusters)}]"
        if empty:
            for k in cc.keys():
                if k not in counter:
                    counter[k] = ""

        options = [
            {
                "label": html.Div(
                    [
                        html.Div(
                            style={"background-color": colour},
                            className="color-rect",
                        ),
                        html.Div(
                            (
                                f"Everything{counter[cluster]}"
                                if cluster == "all"
                                else f"Cluster #{i}{counter[cluster]}"
                            ),
                            style={
                                "display": "inline-block",
                                "padding-left": 10,
                            },
                        ),
                    ],
                    style={"display": "flex", "align-items": "center"},
                ),
                "value": cluster,
            }
            for i, (cluster, colour) in enumerate(cluster_colours().items())
            if cluster in counter
        ]
        return options

    @classmethod
    def register_callbacks(
        cls,
        app: Dash,
        id: Union[None, str, Dict] = None,
        empty: bool = False,
    ):
        """Register callbacks for the cluster dropdowns.
        This is only needed if the id is changed (otherwise it is already setup).

        Args:
            app: Dash app
            id: Custom id (dicts should have an `ALL` component). Defaults to None.
            empty: Include empty clausers. Defaults to False.
        """
        if id is None:
            id = cls.get_id(ALL)

        @app.callback(
            Output(id, "options"),
            Input("auxiliary_store", "data"),
            prevent_initial_call=False,
        )
        def cluster_dropdown_count_callback(aux):
            if aux is None:
                return no_update
            clusters = get_clusters(aux)
            options = cls.get_options(clusters, empty)
            if isinstance(id, dict):
                return [options] * len(ctx.outputs_list)
            else:
                return options


class DeleteButton(html.Button):
    def __init__(self, index: Any, children: str = "x", **kwargs: Any):
        """Create a delete button.

        Args:
            index: Which index should be deleted.
            children: The visuals of the button. Defaults to "x".
            **kwargs: additional arguments forwarded to `html.Button`.
        """
        super().__init__(
            children=children,
            id=generate_id(DeleteButton, index),
            className="delete",
            **kwargs,
        )


try:
    import kaleido  # noqa: F401

    class PdfButton(html.Button):
        def __init__(
            self,
            index: str,
            plot_name: str,
            children: str = "Download as pdf",
            className: str = "pdf_button",
            **kwargs: Any,
        ):
            """Create a button for donwloading plots as pdf.

            Args:
                index: Which plot should be downloaded.
                children: The text of the button. Defaults to
                    "Download as pdf".
                **kwargs: additional arguments forwarded to `html.Button`.
            """
            id = generate_id(type(self), index)
            id["plot"] = plot_name
            id2 = generate_id(type(self), index, "download")
            id2["plot"] = plot_name
            children = [children, dcc.Download(id=id2)]
            super().__init__(
                children=children, id=id, className=className, **kwargs
            )

        @classmethod
        def register_callback(
            cls, app: Dash, plot_name: str, graph_id: Dict[str, str]
        ):
            """Register callbacks.
            NOTE: Currently this method has to be called separately for every
            type of graph.
            This is because Dash cannot match based on properties (i.e.,
            select only the `State`s with a "figure" property).

            Args:
                app: Xiplot app.
                plot_name: Name of the plot.
                graph_id: Id of the graph.
            """
            id = generate_id(cls, MATCH)
            id["plot"] = plot_name
            id2 = generate_id(cls, MATCH, "download")
            id2["plot"] = plot_name
            graph_id["index"] = MATCH

            @app.callback(
                Output(id2, "data"),
                Input(id, "n_clicks"),
                State(graph_id, "figure"),
                prevent_initial_call=True,
            )
            def download_as_pdf(n_clicks, figure):
                if not figure:
                    return no_update
                fig_img = po.io.to_image(figure, format="pdf")
                file = BytesIO(fig_img)
                encoded = base64.b64encode(file.getvalue()).decode("ascii")
                return dict(
                    base64=True,
                    content=encoded,
                    filename="xiplot.pdf",
                    type="application/pdf",
                )

except ImportError:

    class PdfButton(html.Div):
        def __init__(
            self,
            index: str,
            plot_name: str,
            children: str = "Download as pdf",
            **kwargs: Any,
        ):
            super().__init__(id=generate_id(type(self), index), **kwargs)

        @classmethod
        def register_callback(
            cls, app: Dash, plot_name: str, graph_id: Dict[str, str]
        ):
            pass


class PlotData(dcc.Store):
    @classmethod
    def get_id(cls, index: Any, plot_name: str) -> Dict[str, Any]:
        id = generate_id(cls, index)
        id["plot"] = plot_name
        return id

    def __init__(self, index: Any, plot_name: str, **kwargs):
        """
        Create a `dcc.Store` for storing plot configurations.
        These are used to save the xiplot state to a file.

        Args:
            index: The plot index.
            plot_name: The plot name (`APlot.name()`).
        """
        super().__init__(
            id=self.get_id(index, plot_name),
            data=dict(index=index, type=plot_name),
            **kwargs,
        )

    @classmethod
    def register_callback(
        cls,
        plot_name: str,
        app: Dash,
        inputs: Union[Dict[str, Union[Input, State]], Any],
        process: Optional[Callable[[Any], Dict[str, Any]]] = None,
    ):
        """Register callbacks for updating whenever the configuration changes.
        NOTE: This method has to be called separately for every type of plot.

        Args:
            plot_name: The plot name (`APlot.name()`).
            app: The xiplot app.
            inputs: Dictionary of `Input`s that control the plot. Note that
                index must be `MATCH`. Example: ```
                dict(
                    var=Input({
                        "type": "var-dropdown", "index": MATCH
                    }, "value")
                )
                ```
            process: Optional function that processes the `inputs` into a
                storable dictionary. Defaults to None.
        """
        # This assert does not verify that 'process' returns a dict
        assert callable(process) or isinstance(inputs, dict), (
            "'inputs' must be a `dict` or 'process' must be a function"
            " returning a `dict`"
        )

        # Try to enforce MATCH on the "index"
        if isinstance(inputs, dict):
            for v in inputs.values():
                v.component_id["index"] = MATCH
        elif isinstance(inputs, Sequence):
            for v in inputs:
                v.component_id["index"] = MATCH
        elif isinstance(inputs, Input):
            inputs.component_id["index"] = MATCH

        id = cls.get_id(MATCH, plot_name)

        @app.callback(
            Output(id, "data"),
            inputs={"meta": State(id, "data"), "inputs": inputs},
            prevent_initial_call=False,
        )
        def update_metadata(meta, inputs):
            if callable(process):
                inputs = process(inputs)
            for key, value in inputs.items():
                meta[key] = value
            return meta


class HelpButton(dcc.ConfirmDialogProvider):
    def __init__(self, text: str, btn_kws: Dict[str, Any] = {}, **kwargs):
        """Create a button that shows a text on hover, and the same text in a
        dialog when clicked.

        Args:
            text: The (help) text to be shown.
            btn_kws: Keyword arguments for the button.
            **kwargs: Keyword arguments for the wrapper.
        """
        super().__init__(
            html.Button("?", title=text, **btn_kws), message=text, **kwargs
        )
