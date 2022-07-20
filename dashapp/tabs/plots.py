from dash import html, dcc, Output, Input, State, ctx, ALL

from dashapp.tabs import Tab
from dashapp.utils.layouts import layout_wrapper
from dashapp.graphs.scatterplot import Scatterplot
from dashapp.graphs.histogram import Histogram
from dashapp.graphs.heatmap import Heatmap
from dashapp.graphs.barplot import Barplot
from dashapp.graphs.table import Table
from dashapp.graphs.smiles import Smiles


class PlotsTab(Tab):
    plot_types = {
        p.name(): p for p in [Scatterplot, Histogram, Heatmap, Barplot, Table, Smiles]
    }

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        for plot_name, plot_type in PlotsTab.plot_types.items():
            plot_type.register_callbacks(
                app, df_from_store=df_from_store, df_to_store=df_to_store
            )

        @app.callback(
            Output("graphs", "children"),
            Input("new_plot-button", "n_clicks"),
            Input({"type": "plot-delete", "index": ALL}, "n_clicks"),
            State("graphs", "children"),
            State("plot_type", "value"),
            Input("data_frame_store", "data"),
            State("clusters_column_store", "data"),
            prevent_initial_call=True,
        )
        def add_new_plot(n_clicks, deletion, children, plot_type, df, kmeans_col):
            if ctx.triggered_id == "data_frame_store":
                return []

            if ctx.triggered_id == "new_plot-button":
                # read df from store
                df = df_from_store(df)
                # create column for clusters if needed
                if len(kmeans_col) == df.shape[0]:
                    df["Clusters"] = kmeans_col
                columns = df.columns.to_list()
                columns.remove("auxiliary")
                layout = PlotsTab.plot_types[plot_type].create_new_layout(
                    n_clicks, df, columns
                )
                children.append(layout)
                return children

            deletion_id = ctx.triggered_id["index"]

            children = [
                chart
                for chart in children
                if chart["props"]["id"]["index"] != deletion_id
            ]

            return children

    @staticmethod
    def create_layout():
        return html.Div(
            [
                layout_wrapper(
                    component=dcc.Dropdown(
                        options=list(PlotsTab.plot_types.keys()), id="plot_type"
                    ),
                    title="Select a plot type",
                    style={"width": "98%"},
                ),
                html.Button("Add", id="new_plot-button"),
            ],
            id="control_plots_content-container",
        )
