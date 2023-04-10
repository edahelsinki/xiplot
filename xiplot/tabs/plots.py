import uuid

import dash
import dash_mantine_components as dmc
import jsonschema
from dash import ALL, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import CycleBreakerInput

from xiplot.plots.barplot import Barplot
from xiplot.plots.heatmap import Heatmap
from xiplot.plots.histogram import Histogram
from xiplot.plots.scatterplot import Scatterplot
from xiplot.plots.smiles import Smiles
from xiplot.plots.table import Table
from xiplot.plugin import get_plugins_cached
from xiplot.tabs import Tab
from xiplot.utils import generate_id
from xiplot.utils.components import DeleteButton, FlexRow
from xiplot.utils.embedding import add_pca_columns_to_df
from xiplot.utils.layouts import layout_wrapper


class Plots(Tab):
    plot_types = {
        p.name(): p
        for p in [Scatterplot, Histogram, Heatmap, Barplot, Table, Smiles]
        + get_plugins_cached("plot")
    }

    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        for plot_name, plot_type in Plots.plot_types.items():
            plot_type.register_callbacks(
                app, df_from_store=df_from_store, df_to_store=df_to_store
            )

        @app.callback(
            Output("plots-tab-settings-session", "children"),
            Output("plots", "children"),
            Output("metadata_store", "data"),
            Output("plots-tab-notify-container", "children"),
            Input("new_plot-button", "n_clicks"),
            Input(generate_id(DeleteButton, ALL), "n_clicks"),
            State("plots", "children"),
            State("plot_type", "value"),
            State("data_frame_store", "data"),
            State("clusters_column_store", "data"),
            State("pca_column_store", "data"),
            CycleBreakerInput("metadata_store", "data"),
            State("plots-tab-settings-session", "children"),
        )
        def add_new_plot(
            n_clicks,
            deletion,
            children,
            plot_type,
            df,
            kmeans_col,
            pca_cols,
            meta,
            last_meta_session,
        ):
            if meta is None:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update

            if not children:
                children = []

            if ctx.triggered_id in [
                "new_plot-button",
                "metadata_store_data_breaker",
            ]:
                if kmeans_col is None:
                    return (
                        meta["session"],
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
                            meta["session"],
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
                elif meta["session"] == last_meta_session:
                    return (
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                    )
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
                                                    type=dict(type="string")
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
                            meta["session"],
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

                if pca_cols and len(pca_cols) == df.shape[0]:
                    df["Xiplot_PCA_1"] = [i[0] for i in pca_cols]
                    df["Xiplot_PCA_2"] = [i[1] for i in pca_cols]

                columns = df.columns.to_list()

                notifications = []

                for index, config in plots.items():
                    plot_type = config["type"]
                    config = {k: v for k, v in config.items() if k != "type"}

                    if not plot_type in Plots.plot_types:
                        notifications.append(
                            dmc.Notification(
                                id=str(uuid.uuid4()),
                                color="yellow",
                                title="Warning",
                                message=f"Unknown plot type: {plot_type}",
                                action="show",
                                autoClose=10000,
                            )
                        )
                        continue

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

                if ctx.triggered_id == "new_plot-button":
                    return meta["session"], children, dash.no_update, notifications
                else:
                    meta["plots"].clear()
                    return meta["session"], children, meta, notifications

            deletion_id = ctx.triggered_id["index"]

            children = [
                chart
                for chart in children
                if chart["props"]["id"]["index"] != deletion_id
            ]

            return meta["session"], children, dash.no_update, None

    @staticmethod
    def create_layout():
        plots = list(Plots.plot_types.keys())
        return html.Div(
            [
                layout_wrapper(
                    component=FlexRow(
                        dcc.Dropdown(plots, plots[0], id="plot_type", clearable=False),
                        html.Button("Add", id="new_plot-button", className="button"),
                    ),
                    title="Select a plot type",
                ),
            ],
            id="control_plots_content-container",
        )

    @staticmethod
    def create_layout_globals():
        return html.Div(
            [
                html.Div(id="plots-tab-notify-container", style={"display": "none"}),
                html.Div(id="plots-tab-settings-session", style={"display": "none"}),
            ],
            style={"display": "none"},
        )
