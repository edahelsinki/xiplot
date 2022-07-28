import numpy as np
import pandas as pd

from dash import html, Output, Input, State, MATCH, ALL, dash_table, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import delete_button
from dashapp.utils.cluster import cluster_colours
from dashapp.graphs import Graph


class Table(Graph):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "table", "index": MATCH}, "data"),
            Output({"type": "table", "index": MATCH}, "sort_by"),
            Input("clusters_column_store", "data"),
            Input("selected_rows_store", "data"),
            State({"type": "table", "index": ALL}, "data"),
        )
        def update_table_data(kmeans_col, selected_rows, df):
            df = df[0]
            df = pd.DataFrame(df)
            df.rename_axis("index_copy")

            if len(kmeans_col) == df.shape[0]:
                df["Clusters"] = kmeans_col

            if ctx.triggered_id == "selected_rows_store" or selected_rows:
                df["Selection"] = selected_rows
                columns = df.columns.to_list()
                return df[columns].to_dict("records"), [
                    {"column_id": "Selection", "direction": "asc"},
                    {"column_id": "index_copy", "direction": "asc"},
                ]
            columns = df.columns.to_list()
            return df[columns].to_dict("records"), [
                {"column_id": "index_copy", "direction": "asc"}
            ]

        @app.callback(
            output=dict(
                selected_rows_store=Output("selected_rows_store", "data"),
                table=Output({"type": "table", "index": ALL}, "selected_rows"),
            ),
            inputs=[
                Input({"type": "table", "index": ALL}, "selected_rows"),
                Input("data_frame_store", "data"),
                Input("selected_rows_store", "data"),
            ],
        )
        def update_selected_rows(selected_rows_checkbox, df, selected_rows):
            trigger = ctx.triggered_id

            if trigger == "selected_rows_store":
                if not selected_rows:
                    raise PreventUpdate()

                result = []
                id = 0
                for s in selected_rows:
                    if not s:
                        result.append(id)
                    id += 1

                tables = len(ctx.outputs_grouping["table"])
                return dict(
                    selected_rows_store=selected_rows,
                    table=[result for _ in range(tables)],
                )

            df = df_from_store(df)

            if trigger == "data_frame_store":
                return dict(selected_rows_store=[True] * df.shape[0], table=[])

            tables = len(ctx.outputs_grouping["table"])

            if selected_rows_checkbox == [None] and False in selected_rows:
                result = []
                id = 0
                for s in selected_rows:
                    if not s:
                        result.append(id)
                    id += 1
                return dict(
                    selected_rows_store=selected_rows,
                    table=[result for _ in range(tables)],
                )

            if not selected_rows_checkbox:
                raise PreventUpdate()
            if selected_rows_checkbox == [None]:
                selected_rows_checkbox = []
            else:
                selected_rows_checkbox = selected_rows_checkbox[0]
            result = [True] * df.shape[0]
            for row in selected_rows_checkbox:
                result[row] = False

            return dict(
                selected_rows_store=result,
                table=[selected_rows_checkbox for _ in range(tables)],
            )

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
            ],
            id={"type": "table-container", "index": index},
            className="graphs",
        )
