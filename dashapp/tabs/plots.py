import uuid

import dash
import dash_mantine_components as dmc

from dash import html, dcc, Output, Input, State, ctx, ALL
from dash.exceptions import PreventUpdate

from dashapp.tabs import Tab
from dashapp.utils.layouts import layout_wrapper
from dashapp.plots.scatterplot import Scatterplot
from dashapp.plots.histogram import Histogram
from dashapp.plots.heatmap import Heatmap
from dashapp.plots.barplot import Barplot
from dashapp.plots.table import Table
from dashapp.plots.smiles import Smiles


class Plots(Tab):
    plot_types = {
        p.name(): p for p in [Scatterplot, Histogram, Heatmap, Barplot, Table, Smiles]
    }

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        for plot_name, plot_type in Plots.plot_types.items():
            plot_type.register_callbacks(
                app, df_from_store=df_from_store, df_to_store=df_to_store
            )

        @app.callback(
            Output("plots", "children"),
            Output("metadata_store", "data"),
            Output("plots-tab-notify-container", "children"),
            Input("new_plot-button", "n_clicks"),
            Input({"type": "plot-delete", "index": ALL}, "n_clicks"),
            State("plots", "children"),
            State("plot_type", "value"),
            State("data_frame_store", "data"),
            State("clusters_column_store", "data"),
            State("metadata_store", "data"),
            Input("metadata_session", "data"),
        )
        def add_new_plot(
            n_clicks,
            deletion,
            children,
            plot_type,
            df,
            kmeans_col,
            meta,
            meta_session,
        ):
            if not children:
                children = []

            if ctx.triggered_id in ["new_plot-button", "metadata_session"]:
                if kmeans_col is None:
                    return (
                        dash.no_update,
                        dash.no_update,
                        dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="yellow",
                            title="Warning",
                            message="You have not yet loaded any data file.",
                            action="show",
                            autoClose=10000,
                        ),
                    )

                if ctx.triggered_id == "new_plot-button":
                    if not plot_type:
                        return (
                            dash.no_update,
                            dash.no_update,
                            dmc.Notification(
                                id=str(uuid.uuid4()),
                                color="yellow",
                                title="Warning",
                                message="You have not selected any plot type.",
                                action="show",
                                autoClose=10000,
                            ),
                        )

                    plots = {str(uuid.uuid4()): dict(type=plot_type)}
                else:
                    children = []

                    plots = meta["plots"]

                    if not isinstance(plots, dict):
                        return (
                            dash.no_update,
                            dash.no_update,
                            dmc.Notification(
                                id=str(uuid.uuid4()),
                                color="yellow",
                                title="Warning",
                                message='The plots tab must be initialised with a map of "plots".',
                                action="show",
                                autoClose=10000,
                            ),
                        )

                    for plot in plots.values():
                        if not isinstance(plot, dict):
                            return (
                                dash.no_update,
                                dash.no_update,
                                dmc.Notification(
                                    id=str(uuid.uuid4()),
                                    color="yellow",
                                    title="Warning",
                                    message="Every plot must be configured with a map.",
                                    action="show",
                                    autoClose=10000,
                                ),
                            )

                        if plot.get("type") is None:
                            return (
                                dash.no_update,
                                dash.no_update,
                                dmc.Notification(
                                    id=str(uuid.uuid4()),
                                    color="yellow",
                                    title="Warning",
                                    message='Every plot must have a "type".',
                                    action="show",
                                    autoClose=10000,
                                ),
                            )

                        if Plots.plot_types.get(plot["type"]) is None:
                            return (
                                dash.no_update,
                                dash.no_update,
                                dmc.Notification(
                                    id=str(uuid.uuid4()),
                                    color="yellow",
                                    title="Warning",
                                    message=f'Unknown plot type "{plot["type"]}".',
                                    action="show",
                                    autoClose=10000,
                                ),
                            )

                # read df from store
                df = df_from_store(df)

                # create column for clusters if needed
                if len(kmeans_col) == df.shape[0]:
                    df["Clusters"] = kmeans_col
                columns = df.columns.to_list()

                for index, config in plots.items():
                    plot_type = config["type"]
                    config = {k: v for k, v in config.items() if k != "type"} or None

                    try:
                        layout = Plots.plot_types[plot_type].create_new_layout(
                            str(uuid.uuid4()),
                            df,
                            columns,
                            config=config,
                        )
                    except Exception as err:
                        return (
                            dash.no_update,
                            dash.no_update,
                            dmc.Notification(
                                id=str(uuid.uuid4()),
                                color="yellow",
                                title="Warning",
                                message=f"Failed to create a {plot_type}: {err}",
                                action="show",
                                autoClose=10000,
                            ),
                        )

                    children.append(layout)

                return children, dash.no_update, None

            deletion_id = ctx.triggered_id["index"]

            children = [
                chart
                for chart in children
                if chart["props"]["id"]["index"] != deletion_id
            ]

            meta["plots"] = {k: v for k, v in meta["plots"].items() if k != deletion_id}

            return children, meta, None

    @staticmethod
    def create_layout():
        return html.Div(
            [
                layout_wrapper(
                    component=dcc.Dropdown(
                        options=list(Plots.plot_types.keys()), id="plot_type"
                    ),
                    title="Select a plot type",
                    style={"width": "98%"},
                ),
                html.Button("Add", id="new_plot-button"),
            ],
            id="control_plots_content-container",
        )

    @staticmethod
    def create_layout_globals():
        return html.Div(id="plots-tab-notify-container", style={"display": "none"})
