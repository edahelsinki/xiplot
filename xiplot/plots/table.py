import numpy as np
import pandas as pd
import re

import dash
import jsonschema

from dash import html, dcc, Output, Input, State, MATCH, ALL, dash_table, ctx, no_update
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import CycleBreakerInput

from xiplot.utils.layouts import delete_button, layout_wrapper
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.dataframe import get_smiles_column_name
from xiplot.utils.table import get_sort_by, get_updated_item, get_updated_item_id
from xiplot.utils.regex import dropdown_regex, get_columns_by_regex
from xiplot.plots import APlot


class Table(APlot):
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
            Input("pca_column_store", "data"),
            prevent_initial_call=False,
        )
        def update_table_data(
            kmeans_col, selected_rows, df, table_df, sort_by, pca_cols
        ):
            # Try branch for testing
            try:
                trigger = ctx.triggered_id
                if trigger == "data_frame_store" or not table_df:
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except:
                trigger = "selected_rows_store"

            table_data = []
            sort_bys = []

            if pca_cols:
                pca1 = [row[0] for row in pca_cols]
                pca2 = [row[1] for row in pca_cols]

            for table_df, sort_by in zip(table_df, sort_by):
                table_df = pd.DataFrame(table_df)
                table_df.rename_axis("index_copy")

                if len(selected_rows) == table_df.shape[0]:
                    table_df["Selection"] = selected_rows
                if len(kmeans_col) == table_df.shape[0]:
                    table_df["Clusters"] = kmeans_col

                sort_by = get_sort_by(sort_by, selected_rows, trigger)

                if pca_cols:
                    if len(pca_cols) == table_df.shape[0]:
                        table_df["Xiplot_PCA_1"] = pca1
                        table_df["Xiplot_PCA_2"] = pca2

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
            if selected_rows_checkbox == [None] or len(selected_rows_checkbox) == 0:
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
            except:
                selected_rows_checkbox = selected_rows_checkbox[0]

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
            prevent_initial_call=False,
        )
        def update_table_checkbox(selected_rows, kmeans_col):
            if not selected_rows:
                raise PreventUpdate()

            result = []
            for id, s in enumerate(selected_rows):
                if not s:
                    result.append(id)

            # Try branch for testing
            try:
                table_amount = len(ctx.outputs_grouping["table"])
            except:
                table_amount = 1

            return dict(table=[result for _ in range(table_amount)])

        @app.callback(
            output=dict(
                cell_store=Output("lastly_clicked_point_store", "data"),
                active_cell=Output({"type": "table", "index": ALL}, "active_cell"),
            ),
            inputs=[
                Input({"type": "table", "index": ALL}, "active_cell"),
                Input({"type": "table", "index": ALL}, "derived_viewport_indices"),
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
                    column = cell["column_id"]
                    break

            smiles_col = get_smiles_column_name(df)

            # Try branch for testing
            try:
                if row is None or column != smiles_col:
                    raise PreventUpdate()
            except:
                pass

            return dict(cell_store=row, active_cell=[None] * len(active_cells))

        @app.callback(
            Output({"type": "table", "index": ALL}, "data"),
            Output({"type": "table", "index": ALL}, "columns"),
            Input({"type": "table_columns_submit-button", "index": ALL}, "n_clicks"),
            State({"type": "table_columns-dd", "index": ALL}, "value"),
            State({"type": "table", "index": ALL}, "columns"),
            State({"type": "table", "index": ALL}, "data"),
            State("data_frame_store", "data"),
            State("clusters_column_store", "data"),
            State("pca_column_store", "data"),
        )
        def update_table_columns(
            n_clicks, dropdown_columns, columns, table_df, df, kmeans_col, pca_cols
        ):
            if not ctx.triggered_id:
                raise PreventUpdate()

            trigger_id = ctx.triggered_id["index"]
            df = df_from_store(df)

            if len(kmeans_col) == df.shape[0]:
                df["Clusters"] = kmeans_col

            if pca_cols and len(pca_cols) == df.shape[0]:
                pca1 = [row[0] for row in pca_cols]
                pca2 = [row[1] for row in pca_cols]

                df["Xiplot_PCA_1"] = pca1
                df["Xiplot_PCA_2"] = pca2

            for id, item in enumerate(ctx.inputs_list[0]):
                if item["id"]["index"] == trigger_id:
                    if n_clicks[id] is None or dropdown_columns[id] is None:
                        raise PreventUpdate()
                    new_columns = get_columns_by_regex(
                        df.columns.to_list(), dropdown_columns[id]
                    )
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
            Input("pca_column_store", "data"),
            State({"type": "table_columns_regex-input", "index": ALL}, "value"),
            State({"type": "table_columns-dd", "index": ALL}, "options"),
            State("data_frame_store", "data"),
            State("clusters_column_store", "data"),
        )
        def add_matching_values(
            n_clicks_all,
            selected_columns_all,
            pca_cols,
            keyword_all,
            columns_all,
            df,
            kmeans_col,
        ):
            df = df_from_store(df)
            if len(kmeans_col) == df.shape[0]:
                df["Clusters"] = kmeans_col

            if pca_cols and len(pca_cols) == df.shape[0]:
                pca1 = [row[0] for row in pca_cols]
                pca2 = [row[1] for row in pca_cols]

                df["Xiplot_PCA_1"] = pca1
                df["Xiplot_PCA_2"] = pca2

            # Try branch for testing
            try:
                id = get_updated_item_id(
                    n_clicks_all, ctx.triggered_id["index"], ctx.inputs_list[0]
                )
            except:
                id = 0

            keyword = keyword_all[id]
            columns = columns_all[id]
            selected_columns = selected_columns_all[id]

            # Try branch for testing
            try:
                try:
                    trigger = ctx.triggered_id["type"]
                except:
                    trigger = ctx.triggered_id
            except:
                trigger = "table_columns_regex-button"

            if trigger == "pca_column_store":
                columns_all = [df.columns.to_list() for i in range(len(columns_all))]
                selected_columns_all = [[] for i in range(len(selected_columns_all))]

                return (
                    columns_all,
                    selected_columns_all,
                    [no_update] * len(n_clicks_all),
                )

            if trigger == "table_columns-dd":
                columns = df.columns.to_list()
                columns, selected_columns, hits = dropdown_regex(
                    columns, selected_columns
                )
                columns_all[id] = columns
                selected_columns_all[id] = selected_columns

                return (
                    columns_all,
                    selected_columns_all,
                    [no_update] * len(n_clicks_all),
                )

            if trigger == "table_columns_regex-button":
                columns, selected_columns, hits = dropdown_regex(
                    columns or [], selected_columns, keyword
                )
            if keyword is None or hits == 0:
                raise PreventUpdate()

            columns_all[id] = columns
            selected_columns_all[id] = selected_columns

            return columns_all, selected_columns_all, [None] * len(n_clicks_all)

        @app.callback(
            output=dict(
                meta=Output("metadata_store", "data"),
            ),
            inputs=[
                State("metadata_store", "data"),
                Input({"type": "table", "index": ALL}, "page_current"),
                Input({"type": "table", "index": ALL}, "filter_query"),
                Input({"type": "table", "index": ALL}, "sort_by"),
                Input({"type": "table", "index": ALL}, "hidden_columns"),
                Input({"type": "table", "index": ALL}, "columns"),
            ],
            prevent_initial_call=False,
        )
        def update_settings(
            meta,
            current_pages,
            filter_queries,
            sort_bys,
            hidden_column_lists,
            column_selections,
        ):
            if meta is None:
                return dash.no_update

            for page_current, filter_query, sort_by, hidden_columns, columns in zip(
                *ctx.args_grouping[1 : 5 + 1]
            ):
                if (
                    not page_current["triggered"]
                    and not filter_query["triggered"]
                    and not sort_by["triggered"]
                    and not hidden_columns["triggered"]
                    and not columns["triggered"]
                ):
                    continue

                index = page_current["id"]["index"]
                page_current = page_current["value"] or 0
                filter_query = filter_query["value"] or ""
                sort_by = {c["column_id"]: c["direction"] for c in sort_by["value"]}
                hidden_columns = hidden_columns["value"]
                columns = [c["id"] for c in columns["value"]]

                meta["plots"][index] = dict(
                    type=Table.name(),
                    columns={
                        c: {
                            "hidden": c in hidden_columns,
                            **{"sorting": sort_by[c] for _ in ((),) if c in sort_by},
                        }
                        for c in columns
                    },
                    query=filter_query,
                    page=page_current,
                )

            return dict(meta=meta)

        return [
            update_table_data,
            update_selected_rows_store,
            update_table_checkbox,
            update_lastly_activated_cell,
            update_table_columns,
            sync_with_input,
            add_matching_values,
            update_settings,
        ]

    @staticmethod
    def create_new_layout(index, df, columns, config=dict()):
        df = df.rename_axis("index_copy")
        columns = df.columns.to_list()

        jsonschema.validate(
            instance=config,
            schema=dict(
                type="object",
                properties=dict(
                    columns=dict(
                        type="object",
                        properties={
                            c: dict(
                                type="object",
                                properties=dict(
                                    hidden=dict(type="boolean"),
                                    sorting=dict(enum=["asc", "desc"]),
                                ),
                            )
                            for c in columns
                        },
                    ),
                    query=dict(type="string"),
                    page=dict(
                        type="integer",
                        minimum=0,
                    ),
                ),
            ),
        )

        if "columns" in config:
            columns = list(config["columns"].keys())
            hidden_columns = [
                c for c, v in config["columns"].items() if v.get("hidden", False)
            ]
            sort_by = [
                dict(column_id=c, direction=v["sorting"])
                for c, v in config["columns"].items()
                if "sorting" in v
            ]
        else:
            columns = columns[:5]

            if "Clusters" not in columns:
                columns.append("Clusters")

            hidden_columns = ["Clusters"]
            sort_by = []

        filter_query = config.get("query", "")
        page_current = config.get("page", 0)

        for c in columns:
            if type(df[c][0]) == np.ndarray:
                df = df.astype({c: str})
        return html.Div(
            children=[
                delete_button("plot-delete", index),
                dash_table.DataTable(
                    id={"type": "table", "index": index},
                    columns=[{"name": c, "id": c, "hideable": True} for c in columns],
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
            className="plots",
        )
