import numpy as np
import pandas as pd
from dash import ALL, MATCH, Input, Output, State, ctx, dash_table, dcc, html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import CycleBreakerInput

from xiplot.plots import APlot
from xiplot.utils.cluster import CLUSTER_COLUMN_NAME, cluster_colours
from xiplot.utils.components import (
    ColumnDropdown,
    DeleteButton,
    FlexRow,
    PlotData,
)
from xiplot.utils.regex import get_columns_by_regex
from xiplot.utils.table import get_sort_by, get_updated_item


class Table(APlot):
    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        @app.callback(
            [
                Output({"type": "table", "index": ALL}, "data"),
                Output({"type": "table", "index": ALL}, "sort_by"),
            ],
            Input("selected_rows_store", "data"),
            State({"type": "table", "index": ALL}, "data"),
            Input({"type": "table", "index": ALL}, "sort_by"),
            prevent_initial_call=False,
        )
        def update_table_data(selected_rows, table_df, sort_by):
            # Try branch for testing
            try:
                trigger = ctx.triggered_id
                if trigger == "data_frame_store" or not table_df:
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except Exception:
                trigger = "selected_rows_store"

            table_data = []
            sort_bys = []

            for table_df, sort_by in zip(table_df, sort_by):
                table_df = pd.DataFrame(table_df)
                table_df.rename_axis("index_copy")

                if len(selected_rows) == table_df.shape[0]:
                    table_df["Selection"] = selected_rows

                sort_by = get_sort_by(sort_by, selected_rows, trigger)

                columns = table_df.columns.to_list()

                table_data.append(table_df[columns].to_dict("records"))
                sort_bys.append(sort_by)

            return table_data, sort_bys

        @app.callback(
            Output("selected_rows_store", "data"),
            Input({"type": "table", "index": ALL}, "selected_rows"),
            State("data_frame_store", "data"),
        )
        def update_selected_rows_store(selected_rows_checkbox, df):
            if (
                selected_rows_checkbox == [None]
                or len(selected_rows_checkbox) == 0
            ):
                raise PreventUpdate()

            df = df_from_store(df)

            # Try branch for testing
            try:
                # check, which table had changed
                selected_rows_checkbox = get_updated_item(
                    selected_rows_checkbox,
                    ctx.triggered_id["index"],
                    ctx.inputs_list[0],
                )
            except Exception:
                selected_rows_checkbox = selected_rows_checkbox[0]

            result = [True] * df.shape[0]
            for row in selected_rows_checkbox:
                result[row] = False

            return result

        @app.callback(
            output=dict(
                table=Output({"type": "table", "index": ALL}, "selected_rows")
            ),
            inputs=[
                CycleBreakerInput("selected_rows_store", "data"),
            ],
            prevent_initial_call=False,
        )
        def update_table_checkbox(selected_rows):
            if not selected_rows:
                raise PreventUpdate()

            result = []
            for id, s in enumerate(selected_rows):
                if not s:
                    result.append(id)

            # Try branch for testing
            try:
                table_amount = len(ctx.outputs_grouping["table"])
            except Exception:
                table_amount = 1

            return dict(table=[result for _ in range(table_amount)])

        @app.callback(
            output=dict(
                cell_store=Output("lastly_clicked_point_store", "data"),
                active_cell=Output(
                    {"type": "table", "index": ALL}, "active_cell"
                ),
            ),
            inputs=[
                Input({"type": "table", "index": ALL}, "active_cell"),
                Input(
                    {"type": "table", "index": ALL}, "derived_viewport_indices"
                ),
                State("data_frame_store", "data"),
            ],
        )
        def update_lastly_activated_cell(active_cells, table_row_indices, df):
            if active_cells == [None]:
                raise PreventUpdate()

            row = None
            for cell, indices in zip(active_cells, table_row_indices):
                if cell:
                    row = indices[cell["row"]]
                    break

            return dict(cell_store=row, active_cell=[None] * len(active_cells))

        @app.callback(
            Output({"type": "table", "index": ALL}, "data"),
            Output({"type": "table", "index": ALL}, "columns"),
            Input(
                {"type": "table_columns_submit-button", "index": ALL},
                "n_clicks",
            ),
            State(cls.get_id(ALL, "columns_dropdown"), "value"),
            State({"type": "table", "index": ALL}, "columns"),
            State({"type": "table", "index": ALL}, "data"),
            State("data_frame_store", "data"),
            State("auxiliary_store", "data"),
        )
        def update_table_columns(
            n_clicks,
            dropdown_columns,
            columns,
            table_df,
            df,
            aux,
        ):
            if not ctx.triggered_id:
                raise PreventUpdate()

            trigger_id = ctx.triggered_id["index"]
            df = df_from_store(df)
            aux = df_from_store(aux)
            df = pd.concat((df, aux), axis=1)

            for id, item in enumerate(ctx.inputs_list[0]):
                if item["id"]["index"] == trigger_id:
                    if n_clicks[id] is None or dropdown_columns[id] is None:
                        raise PreventUpdate()
                    new_columns = get_columns_by_regex(
                        df.columns.to_list(), dropdown_columns[id]
                    )
                    columns[id] = [
                        {"name": c, "id": c, "hideable": True}
                        for c in new_columns
                    ]
                    table_df[id] = df[new_columns].to_dict("records")
                    break

            return table_df, columns

        ColumnDropdown.register_callback(
            app,
            cls.get_id(MATCH, "columns_dropdown"),
            df_from_store,
            regex_button_id=cls.get_id(MATCH, "regex_button"),
            regex_input_id=cls.get_id(MATCH, "regex_input"),
        )

        PlotData.register_callback(
            cls.name(),
            app,
            dict(
                page=Input({"type": "table", "index": ALL}, "page_current"),
                query=Input({"type": "table", "index": ALL}, "filter_query"),
                sort_by=Input({"type": "table", "index": ALL}, "sort_by"),
                hidden=Input(
                    {"type": "table", "index": ALL}, "hidden_columns"
                ),
                columns=Input({"type": "table", "index": ALL}, "columns"),
                dropdown=Input(cls.get_id(MATCH, "columns_dropdown"), "value"),
            ),
            lambda inputs: dict(
                columns={
                    column: {
                        "hidden": column in inputs["hidden"],
                        **{
                            "sorting": sb["direction"]
                            for sb in inputs["sort_by"]
                            if column == sb["column_id"]
                        },
                    }
                    for column in [c["id"] for c in inputs["columns"]]
                },
                query=inputs["query"] or "",
                page=inputs["page"] or 0,
                dropdown=inputs["dropdown"],
            ),
        )

        return [
            update_table_data,
            update_selected_rows_store,
            update_table_checkbox,
            update_lastly_activated_cell,
            update_table_columns,
        ]

    @classmethod
    def create_new_layout(cls, index, df, columns, config=dict()):
        df = df.rename_axis("index_copy")
        columns = df.columns.to_list()

        if "columns" in config:
            columns = list(config["columns"].keys())
            hidden_columns = [
                c
                for c, v in config["columns"].items()
                if v.get("hidden", False)
            ]
            sort_by = [
                dict(column_id=c, direction=v["sorting"])
                for c, v in config["columns"].items()
                if "sorting" in v
            ]
        else:
            columns = columns[:5]

            if CLUSTER_COLUMN_NAME not in columns:
                columns.append(CLUSTER_COLUMN_NAME)

            hidden_columns = [CLUSTER_COLUMN_NAME]
            sort_by = []

        filter_query = config.get("query", "")
        page_current = config.get("page", 0)

        for c in columns:
            if type(df[c][0]) == np.ndarray:
                df = df.astype({c: str})
        return html.Div(
            children=[
                DeleteButton(index),
                dash_table.DataTable(
                    id={"type": "table", "index": index},
                    columns=[
                        {"name": c, "id": c, "hideable": True} for c in columns
                    ],
                    hidden_columns=hidden_columns,
                    data=df[columns].to_dict("records"),
                    editable=False,
                    page_action="native",
                    page_size=25,
                    page_current=page_current,
                    sort_action="native",
                    sort_mode="multi",
                    sort_by=sort_by,
                    row_selectable="multi",
                    filter_action="native",
                    filter_query=filter_query,
                    fixed_rows={"headers": True},
                    style_as_list_view=True,
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "height": "auto",
                        "minWidth": "180px",
                        "width": "180px",
                        "maxWidth": "180px",
                        "whiteSpace": "normal",
                        "wordBreak": "break-all",
                    },
                    style_data_conditional=[
                        {
                            "if": {
                                "filter_query": (
                                    f'{{{CLUSTER_COLUMN_NAME}}} = "{cluster}"'
                                ),
                            },
                            "backgroundColor": colour,
                            "color": "black",
                        }
                        for cluster, colour in cluster_colours().items()
                        if cluster != "all"
                    ],
                ),
                FlexRow(
                    ColumnDropdown(
                        cls.get_id(index, "columns_dropdown"),
                        multi=True,
                        options=df.columns,
                        placeholder="Select Columns...",
                        value=config.get("dropdown", None),
                    ),
                    html.Button(
                        "Add columns by regex",
                        id=cls.get_id(index, "regex_button"),
                        className="button",
                    ),
                    html.Button(
                        "Update table",
                        id={
                            "type": "table_columns_submit-button",
                            "index": index,
                        },
                        className="button",
                    ),
                ),
                dcc.Input(
                    id=cls.get_id(index, "regex_input"),
                    style={"display": "none"},
                ),
                PlotData(index, cls.name()),
            ],
            id={"type": "table-container", "index": index},
            className="plots",
        )
