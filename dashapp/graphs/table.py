import numpy as np
import pandas as pd

from dash import html, Output, Input, State, MATCH, ALL, dash_table, ctx
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import CycleBreakerInput

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
            Input("data_frame_store", "data"),
            State({"type": "table", "index": ALL}, "data"),
        )
        def update_table_data(kmeans_col, selected_rows, df, table_df):
            if ctx.triggered_id == "data_frame_store":
                raise PreventUpdate()

            table_df = table_df[0]
            table_df = pd.DataFrame(table_df)
            table_df.rename_axis("index_copy")

            if len(kmeans_col) == table_df.shape[0]:
                table_df["Clusters"] = kmeans_col

            if ctx.triggered_id == "selected_rows_store" or selected_rows:
                table_df["Selection"] = selected_rows
                columns = table_df.columns.to_list()
                return table_df[columns].to_dict("records"), [
                    {"column_id": "Selection", "direction": "asc"},
                    {"column_id": "index_copy", "direction": "asc"},
                ]
            columns = table_df.columns.to_list()
            return table_df[columns].to_dict("records"), [
                {"column_id": "index_copy", "direction": "asc"}
            ]

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
            selected_rows_checkbox = selected_rows_checkbox[0]
            if selected_rows_checkbox is None:
                selected_rows_checkbox = []

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
