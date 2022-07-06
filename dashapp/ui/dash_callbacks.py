import base64
import os

import pandas as pd
import numpy as np

from io import BytesIO

from dash import Output, Input, State, ctx
from dash.exceptions import PreventUpdate
from prometheus_client import Histogram

from dashapp.services.data_frame import (
    read_data_file,
    read_dataframe_with_extension,
    get_kmean,
    get_data_files,
)
from dashapp.services.graphs import *
from dashapp.services.dash_layouts import (
    control_data_content,
    control_plots_content,
    control_clusters_content,
)
from dashapp.ui.dash_renderer import render_smiles


class Callbacks:
    def __init__(self, plot_types) -> None:
        self.__plot_types = plot_types

    def init_callbacks(self, app):
        @app.callback(
            Output("control_data_content-container", "style"),
            Output("control_plots_content-container", "style"),
            Output("control_clusters_content-container", "style"),
            Input("control-tabs", "value"),
        )
        def control(tab):
            style = {"padding-left": "2%"}
            hide_style = {"display": "none"}
            if tab == "control-data-tab":
                return style, hide_style, hide_style
            elif tab == "control-plots-tab":
                return hide_style, style, hide_style
            elif tab == "control-clusters-tab":
                style["padding-top"] = "2%"
                return hide_style, hide_style, style

        try:
            import dash_uploader as du

            @du.callback(
                output=[
                    Output("uploaded_data_file_store", "data"),
                    Output("data_files", "options"),
                    Output("data_files", "value"),
                ],
                id="file_uploader",
            )
            def upload(status):
                filename = os.path.split(status[0])[1]
                df = read_data_file(filename)
                files = get_data_files() + [filename + " (Uploaded)"]
                df = df.to_json(date_format="iso", orient="split")
                os.remove(os.path.join("data", filename))
                return df, files, filename + " (Uploaded)"

        except ImportError:

            @app.callback(
                Output("uploaded_data_file_store", "data"),
                Output("data_files", "options"),
                Output("data_files", "value"),
                Input("file_uploader", "contents"),
                State("file_uploader", "filename"),
            )
            def upload(contents, filename):
                if contents is None:
                    raise PreventUpdate()

                content_type, content_string = contents.split(",")
                decoded = base64.b64decode(content_string)

                df = read_dataframe_with_extension(BytesIO(decoded), filename)

                if df is None:
                    raise PreventUpdate()
                else:
                    files = get_data_files() + [filename + " (Uploaded)"]
                    df = df.to_json(date_format="iso", orient="split")
                    return df, files, filename + " (Uploaded)"

        @app.callback(
            Output("data_frame_store", "data"),
            Output("data_file_store", "data"),
            Output("data_file_load_message-container", "style"),
            Output("data_file_load_message", "children"),
            Output("cluster_feature", "options"),
            Input("submit-button", "n_clicks"),
            Input("uploaded_data_file_store", "data"),
            State("data_files", "value"),
            prevent_initial_call=True,
        )
        def choose_file(
            data_btn,
            uploaded_data,
            filename,
        ):
            trigger = ctx.triggered_id
            if trigger == "submit-button":

                if filename.endswith(" (Uploaded)"):
                    df = pd.read_json(uploaded_data, orient="split")
                    df_store = uploaded_data

                else:
                    df = read_data_file(filename)
                    df_store = df.to_json(date_format="iso", orient="split")
                file_message = f"Data file {filename} loaded successfully!"

            elif trigger == "uploaded_data_file_store":
                df_store = uploaded_data
                df = pd.read_json(uploaded_data, orient="split")
                filename = filename[:-11]
                file_message = f"Data file {filename} loaded successfully!"

            file_style = {"display": "inline"}
            columns = df.columns.to_list()
            return (
                df_store,
                filename,
                file_style,
                file_message,
                columns,
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
            df = pd.read_json(df, orient="split")
            # create column for clusters if needed
            if kmeans_col:
                if len(kmeans_col) == df.shape[0]:
                    df["Clusters"] = kmeans_col
                    df["Clusters"] = df["Clusters"].astype(str)
            columns = df.columns.to_list()
            plot = self.__plot_types[plot_type]
            plot.set_df(df)
            layout = plot.get_layout(n_clicks, columns)

            # TODO other plots as well

            children.append(layout)
            return children

        @app.callback(
            Output("clusters_column_store", "data"),
            Output("clusters_created_message-container", "style"),
            Output("clusters_created_message", "children"),
            Input("cluster-button", "n_clicks"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def set_clusters(n_clicks, n_clusters, features, df):
            df = pd.read_json(df, orient="split")
            kmeans_col = get_kmean(df, int(n_clusters), features)
            style = {"display": "inline"}
            message = "Clusters created!"
            return kmeans_col, style, message

        @app.callback(
            Output("histogram", "figure"),
            Output("histogram", "style"),
            Output("histogram-container", "style"),
            Output("histo_mean", "children"),
            Output("histo_deviation", "children"),
            Input("x_axis_histo", "value"),
            Input("scatterplot", "selectedData"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def render_histogram(x_axis, slct_data, df):
            # FIXME: hide histogram when selection is None?
            df = pd.read_json(df, orient="split")
            if slct_data is None:
                raise PreventUpdate()

            if "Clusters" in df.columns.to_list():
                df["Clusters"] = df["Clusters"].astype(float)

            fig = Histogram(df=df, x_axis=x_axis, barmode="overlay")
            style = fig.style
            div_style = fig.div_style

            points = [point["pointIndex"] for point in slct_data["points"]]
            selected_df = df.loc[df.index.isin(points)]
            color = px.colors.qualitative.Dark2
            fig_2 = Histogram(selected_df, x_axis, color_dicrete_sequence=color)
            fig_2 = fig_2.create_plot().data[0]
            fig = fig.add_trace(fig.create_plot(), fig_2)

            mean = round(df[x_axis].mean(), 3)
            deviation = round(df[x_axis].std(), 3)
            selected_mean = round(selected_df[x_axis].mean(), 3)
            selected_deviation = round(selected_df[x_axis].std(), 3)
            return (
                fig,
                style,
                div_style,
                f"Full mean: {mean}, Selected mean: {selected_mean}",
                f"Full deviation: {deviation}, Selected deviation: {selected_deviation}",
            )
