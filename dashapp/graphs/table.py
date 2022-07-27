import plotly.express as px
import numpy as np
import pandas as pd

from dash import html, Output, Input, State, MATCH, ALL, dash_table, ctx
from dash.exceptions import PreventUpdate

from dashapp.utils.layouts import delete_button
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
            prevent_initial_call=True,
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
            Output("selected_rows_store", "data"),
            Input({"type": "table", "index": ALL}, "selected_rows"),
            Input("data_frame_store", "data"),
            State("selected_rows_store", "data"),
            prevent_initial_call=True,
        )
        def update_selected_rows(selected_rows_checkbox, df, selected_rows):
            df = df_from_store(df)
            if ctx.triggered_id == "data_frame_store":
                return [True] * df.shape[0]
            if selected_rows_checkbox == []:
                raise PreventUpdate()
            if selected_rows_checkbox[-1] is None:
                raise PreventUpdate()
            if selected_rows and len(selected_rows_checkbox[0]) == selected_rows.count(
                False
            ):
                raise PreventUpdate()
            selected_rows = selected_rows_checkbox[0]
            result = [True] * df.shape[0]
            for row in selected_rows:
                result[row] = False
            return result

        @app.callback(
            output=dict(
                table=Output({"type": "table", "index": ALL}, "selected_rows"),
                scatter=Output({"type": "scatterplot", "index": ALL}, "clickData"),
            ),
            inputs=[
                Input({"type": "scatterplot", "index": ALL}, "clickData"),
                State({"type": "table", "index": ALL}, "selected_rows"),
            ],
            prevent_initial_call=True,
        )
        def update_tables_selected_rows(click, selected_rows):
            if selected_rows == [None]:
                selected_rows = []
            else:
                selected_rows = selected_rows[0]
            # go through all the scatterplots to avoid getting NoneType error
            for c in click:
                if c:
                    row = c["points"][0]["customdata"][0]["index"]
            if row not in selected_rows:
                selected_rows.append(row)
            else:
                selected_rows.remove(row)
            table_amount = len(ctx.outputs_grouping["table"])
            scatter_amount = len(ctx.outputs_grouping["scatter"])
            return dict(
                table=[selected_rows for _ in range(table_amount)],
                scatter=[None] * scatter_amount,
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
                                "filter_query": '{Clusters} = "all"',
                            },
                            "backgroundColor": px.colors.qualitative.Plotly[0],
                            "color": "white",
                        },
                    ]
                    + [
                        {
                            "if": {
                                "filter_query": f'{{Clusters}} = "c{i+1}"',
                            },
                            "backgroundColor": c,
                        }
                        for i, c in enumerate(px.colors.qualitative.Plotly[1:])
                    ],
                ),
            ],
            id={"type": "table-container", "index": index},
            className="graphs",
        )
