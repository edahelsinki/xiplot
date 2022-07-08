from dash import html, dcc, Output, Input, State

from dashapp.tabs import Tab
from dashapp.utils.layouts import layout_wrapper
from dashapp.graphs.scatterplot import Scatterplot
from dashapp.graphs.histogram import Histogram
from dashapp.graphs.heatmap import Heatmap
from dashapp.graphs.barplot import Barplot


class PlotsTab(Tab):
    plot_types = {p.name(): p for p in [Scatterplot, Histogram, Heatmap, Barplot]}

    @staticmethod
    def name() -> str:
        return "Plots"

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        for plot_name, plot_type in PlotsTab.plot_types.items():
            plot_type.register_callbacks(
                app, df_from_store=df_from_store, df_to_store=df_to_store
            )

        @app.callback(
            Output("main", "children"),
            Input("new_plot-button", "n_clicks"),
            State("main", "children"),
            State("plot_type", "value"),
            State("data_frame_store", "data"),
            State("clusters_column_store", "data"),
            prevent_initial_call=True,
        )
        def add_new_plot(n_clicks, children, plot_type, df, kmeans_col):
            # read df from store
            df = df_from_store(df)
            # create column for clusters if needed
            if kmeans_col:
                if len(kmeans_col) == df.shape[0]:
                    df["Clusters"] = kmeans_col
            columns = df.columns.to_list()
            layout = PlotsTab.plot_types[plot_type].create_new_layout(
                n_clicks, df, columns
            )
            children.append(layout)
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
