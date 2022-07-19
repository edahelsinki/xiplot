import plotly.express as px

from dash import html, dcc, Output, Input, State, MATCH, dash_table

from dashapp.utils.layouts import delete_button
from dashapp.graphs import Graph


class Table(Graph):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        @app.callback(
            Output({"type": "table", "index": MATCH}, "data"),
            Input("clusters_column_store", "data"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def update_table_data(kmeans_col, df):
            df = df_from_store(df)

            if len(kmeans_col) == df.shape[0]:
                df["Clusters"] = kmeans_col

            columns = df.columns.to_list()
            columns.remove("auxiliary")

            return df[columns].to_dict("records")

    @staticmethod
    def create_new_layout(index, df, columns):
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
