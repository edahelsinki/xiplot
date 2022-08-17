import uuid

import dash
import dash_mantine_components as dmc
import jsonschema

from dash import html, dcc, Output, Input, State, ctx, ALL
from dash.exceptions import PreventUpdate

from xiplot.tabs import Tab
from xiplot.utils.layouts import layout_wrapper
from xiplot.plots.scatterplot import Scatterplot
from xiplot.plots.histogram import Histogram
from xiplot.plots.heatmap import Heatmap
from xiplot.plots.barplot import Barplot
from xiplot.plots.table import Table
from xiplot.plots.smiles import Smiles


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

                    try:
                        jsonschema.validate(
                            instance=meta,
                            schema=dict(
                                type="object",
                                properties=dict(
                                    plots=dict(
                                        type="object",
                                        patternProperties={
                                            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$": dict(
                                                type="object",
                                                properties=dict(
                                                    type=dict(
                                                        enum=list(
                                                            Plots.plot_types.keys()
                                                        )
                                                    ),
                                                ),
                                                required=["type"],
                                            ),
                                        },
                                        additionalProperties=False,
                                    ),
                                ),
                                required=["plots"],
                            ),
                        )
                    except jsonschema.exceptions.ValidationError as err:
                        return (
                            dash.no_update,
                            dash.no_update,
                            dmc.Notification(
                                id=str(uuid.uuid4()),
                                color="yellow",
                                title="Warning",
                                message=f"Invalid plots configuration at meta{err.json_path[1:]}: {err.message}.",
                                action="show",
                                autoClose=10000,
                            ),
                        )

                    plots = meta["plots"]

                # read df from store
                df = df_from_store(df)

                # create column for clusters if needed
                if len(kmeans_col) == df.shape[0]:
                    df["Clusters"] = kmeans_col
                columns = df.columns.to_list()

                notifications = []

                for index, config in plots.items():
                    plot_type = config["type"]
                    config = {k: v for k, v in config.items() if k != "type"}

                    try:
                        layout = Plots.plot_types[plot_type].create_new_layout(
                            index,
                            df,
                            columns,
                            config=config,
                        )

                        children.append(layout)
                    except jsonschema.exceptions.ValidationError as err:
                        notifications.append(
                            dmc.Notification(
                                id=str(uuid.uuid4()),
                                color="yellow",
                                title="Warning",
                                message=f"Invalid configuration for a {plot_type} at meta.plots.{index}{err.json_path[1:]}: {err.message}",
                                action="show",
                                autoClose=10000,
                            )
                        )
                    except ImportError as err:
                        raise err
                    except Exception as err:
                        notifications.append(
                            dmc.Notification(
                                id=str(uuid.uuid4()),
                                color="yellow",
                                title="Warning",
                                message=f"Failed to create a {plot_type}: {err}.",
                                action="show",
                                autoClose=10000,
                            )
                        )

                return children, dash.no_update, notifications

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
