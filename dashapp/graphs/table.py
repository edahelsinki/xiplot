import numpy as np
import pandas as pd
import re

from dash import html, dcc, Output, Input, State, MATCH, ALL, dash_table, ctx, no_update
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import CycleBreakerInput

from dashapp.utils.layouts import delete_button, layout_wrapper
from dashapp.utils.cluster import cluster_colours
from dashapp.utils.dataframe import get_smiles_column_name
from dashapp.utils.table import get_sort_by, get_updated_item, get_updated_item_id
from dashapp.utils.dcc import dropdown_regex
from dashapp.graphs import Graph


class Table(Graph):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            [
                Output({"type": "table", "index": ALL}, "data"),
                Output({"type": "table", "index": ALL}, "sort_by"),
            ],
            State("clusters_column_store", "data"),
            Input("selected_rows_store", "data"),
            Input("data_frame_store", "data"),
            State({"type": "table", "index": ALL}, "data"),
            Input({"type": "table", "index": ALL}, "sort_by"),
        )
        def update_table_data(kmeans_col, selected_rows, df, table_df, sort_by):
            trigger = ctx.triggered_id
            if trigger == "data_frame_store" or not table_df:
                raise PreventUpdate()
            table_amount = len(table_df)

            table_df = table_df[0]
            table_df = pd.DataFrame(table_df)
            table_df.rename_axis("index_copy")
            table_df["Selection"] = selected_rows

            # TODO make a new store for sort by
            sort_by = sort_by[0]

            if len(kmeans_col) == table_df.shape[0]:
                table_df["Clusters"] = kmeans_col

            sort_by = get_sort_by(sort_by, selected_rows, trigger)

            columns = table_df.columns.to_list()
            return [table_df[columns].to_dict("records")] * table_amount, [
                sort_by
            ] * table_amount

        @app.callback(
            Output("selected_rows_store", "data"),
            Input("data_frame_store", "data"),
        )
        def initialize_selected_rows(df):
            df = df_from_store(df)
            return [True] * df.shape[0]

        @app.callback(
            Output("selected_rows_store", "data"),
            Input({"type": "table", "index": ALL}, "selected_rows"),
            State("data_frame_store", "data"),
        )
        def update_selected_rows_store(selected_rows_checkbox, df):
            if selected_rows_checkbox == [None] or len(selected_rows_checkbox) == 0:
                raise PreventUpdate()

            df = df_from_store(df)

            # check, which table had changed
            selected_rows_checkbox = get_updated_item(
                selected_rows_checkbox, ctx.triggered_id["index"], ctx.inputs_list[0]
            )

            result = [True] * df.shape[0]
            for row in selected_rows_checkbox:
                result[row] = False

            return result

        @app.callback(
            output=dict(table=Output({"type": "table", "index": ALL}, "selected_rows")),
            inputs=[
                CycleBreakerInput("selected_rows_store", "data"),
                Input("clusters_column_store", "data"),
            ],
        )
        def update_table_checkbox(selected_rows, kmeans_col):
            if not selected_rows:
                raise PreventUpdate()

            result = []
            for id, s in enumerate(selected_rows):
                if not s:
                    result.append(id)

            tables = len(ctx.outputs_grouping["table"])
            return dict(table=[result for _ in range(tables)])

        @app.callback(
            output=dict(
                cell_store=Output("lastly_clicked_point_store", "data"),
                active_cell=Output({"type": "table", "index": ALL}, "active_cell"),
            ),
            inputs=[
                Input({"type": "table", "index": ALL}, "active_cell"),
                State("data_frame_store", "data"),
            ],
        )
        def update_lastly_activated_cell(active_cells, df):
            if active_cells == [None]:
                raise PreventUpdate()

            row = None
            for cell in active_cells:
                if cell:
                    row = cell["row"]
                    column = cell["column_id"]
                    break

            smiles_col = get_smiles_column_name(df)
            if row is None or column != smiles_col:
                raise PreventUpdate()
            return dict(cell_store=row, active_cell=[None] * len(active_cells))

        @app.callback(
            Output({"type": "table", "index": ALL}, "data"),
            Output({"type": "table", "index": ALL}, "columns"),
            Input({"type": "table_columns_submit-button", "index": ALL}, "n_clicks"),
            State({"type": "table_columns-dd", "index": ALL}, "value"),
            State({"type": "table", "index": ALL}, "columns"),
            State({"type": "table", "index": ALL}, "data"),
            State("data_frame_store", "data"),
        )
        def update_table_columns(n_clicks, dropdown_columns, columns, table_df, df):
            if not ctx.triggered_id:
                raise PreventUpdate()
            trigger_id = ctx.triggered_id["index"]
            df = df_from_store(df)

            for id, item in enumerate(ctx.inputs_list[0]):
                if item["id"]["index"] == trigger_id:
                    if n_clicks[id] is None or dropdown_columns[id] is None:
                        raise PreventUpdate()
                    new_columns = []
                    for dc in dropdown_columns[id]:
                        if " (regex)" in dc:
                            for c in df.columns:
                                if re.search(dc[:-8], c) and c not in new_columns:
                                    new_columns.append(c)
                        elif dc not in new_columns:
                            new_columns.append(dc)
                    columns[id] = [
                        {"name": c, "id": c, "hideable": True} for c in new_columns
                    ]
                    table_df[id] = df[new_columns].to_dict("records")
                    break

            return table_df, columns

        @app.callback(
            Output({"type": "table_columns_regex-input", "index": MATCH}, "value"),
            Input({"type": "table_columns-dd", "index": MATCH}, "search_value"),
        )
        def sync_with_input(keyword):
            if keyword == "":
                raise PreventUpdate()
            return keyword

        @app.callback(
            Output({"type": "table_columns-dd", "index": ALL}, "options"),
            Output({"type": "table_columns-dd", "index": ALL}, "value"),
            Output({"type": "table_columns-dd", "index": ALL}, "search_value"),
            Input({"type": "table_columns_regex-button", "index": ALL}, "n_clicks"),
            Input({"type": "table_columns-dd", "index": ALL}, "value"),
            State({"type": "table_columns_regex-input", "index": ALL}, "value"),
            State({"type": "table_columns-dd", "index": ALL}, "options"),
            State("data_frame_store", "data"),
        )
        def add_matching_values(
            n_clicks_all, dropdown_columns_all, keyword_all, options_all, df
        ):
            df = df_from_store(df)
            id = get_updated_item_id(
                n_clicks_all, ctx.triggered_id["index"], ctx.inputs_list[0]
            )
            keyword = keyword_all[id]
            options = options_all[id]
            columns = dropdown_columns_all[id]

            trigger = ctx.triggered_id["type"]
            if trigger == "table_columns-dd":
                options = df.columns.to_list()
                options.remove("auxiliary")
                options, columns, hits = dropdown_regex(options, columns)
                options_all[id] = options
                dropdown_columns_all[id] = columns
                # TODO change variable names to clearer names
                return (
                    options_all,
                    dropdown_columns_all,
                    [no_update] * len(n_clicks_all),
                )

            if trigger == "table_columns_regex-button":
                options, columns, hits = dropdown_regex(options or [], columns, keyword)
            if keyword is None or hits == 0:
                raise PreventUpdate()

            options_all[id] = options
            dropdown_columns_all[id] = columns

            return options_all, dropdown_columns_all, [None] * len(n_clicks_all)

    @staticmethod
    def create_new_layout(index, df, columns):
        df = df.rename_axis("index_copy")

        columns = df.columns.to_list()
        columns.remove("auxiliary")

        columns = columns[:5] + ["Clusters"]

        for c in columns:
            if type(df[c][0]) == np.ndarray:
                df = df.astype({c: str})
        return html.Div(
            children=[
                delete_button("plot-delete", index),
                dash_table.DataTable(
                    id={"type": "table", "index": index},
                    columns=[{"name": c, "id": c, "hideable": True} for c in columns],
                    data=df[columns].to_dict("records"),
                    editable=False,
                    page_action="native",
                    page_size=25,
                    sort_action="native",
                    sort_mode="multi",
                    sort_by=[],
                    row_selectable="multi",
                    filter_action="native",
                    fixed_rows={"headers": True},
                    style_as_list_view=True,
                    css=[
                        {
                            "selector": ".dash-spreadsheet-menu",
                            "rule": "position: absolute; bottom: 7px",
                        },
                    ],
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
                                "filter_query": f'{{Clusters}} = "{cluster}"',
                            },
                            "backgroundColor": colour,
                            "color": "white" if cluster == "all" else "black",
                        }
                        for cluster, colour in cluster_colours().items()
                    ],
                ),
                layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "table_columns-dd", "index": index},
                        multi=True,
                        options=df.columns,
                    ),
                    css_class="dd-double-right",
                    title="Select columns",
                ),
                html.Button(
                    "Add columns by regex",
                    id={"type": "table_columns_regex-button", "index": index},
                ),
                dcc.Input(
                    id={"type": "table_columns_regex-input", "index": index},
                    style={"display": "none"},
                ),
                html.Button(
                    "Select", id={"type": "table_columns_submit-button", "index": index}
                ),
            ],
            id={"type": "table-container", "index": index},
            className="graphs",
        )