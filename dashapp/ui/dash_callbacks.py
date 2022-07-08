import base64
import os

import pandas as pd

from io import BytesIO

from dash import Output, Input, State, ctx, ALL
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput

from dashapp.services.data_frame import (
    read_data_file,
    read_dataframe_with_extension,
    get_kmean,
    get_data_files,
)
from dashapp.services.dash_layouts import (
    control_data_content,
    control_plots_content,
    control_clusters_content,
)


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
                    ServersideOutput("uploaded_data_file_store", "data"),
                    Output("data_files", "options"),
                    Output("data_files", "value"),
                ],
                id="file_uploader",
            )
            def upload(status):
                filename = os.path.split(status[0])[1]
                df = read_dataframe_with_extension(f"uploads/{filename}", filename)
                files = get_data_files() + [filename + " (Uploaded)"]
                df = df.to_json(date_format="iso", orient="split")
                os.remove(os.path.join("uploads", filename))
                return df, files, filename + " (Uploaded)"

        except ImportError:

            @app.callback(
                ServersideOutput("uploaded_data_file_store", "data"),
                Output("data_files", "options"),
                Output("data_files", "value"),
                Output("file_uploader", "contents"),
                Output("file_uploader", "filename"),
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
                    return df, files, filename + " (Uploaded)", None, None

        @app.callback(
            ServersideOutput("data_frame_store", "data"),
            ServersideOutput("data_file_store", "data"),
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
            df_store = pd.read_json(df_store, orient="split")
            df_store["auxiliary"] = [{"index": i} for i in range(len(df))]
            df_store = df_store.to_json(date_format="iso", orient="split")
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
            columns = df.columns.to_list()
            plot = self.__plot_types[plot_type](df)
            layout = plot.get_layout(n_clicks, df, columns)
            children.append(layout)
            return children

        @app.callback(
            ServersideOutput("clusters_column_store", "data"),
            Output("clusters_created_message-container", "style"),
            Output("clusters_created_message", "children"),
            Input("cluster-button", "n_clicks"),
            Input({"type": "scatterplot", "index": ALL}, "selectedData"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
            State("data_frame_store", "data"),
            State("clusters_column_store", "data"),
            State("selection_cluster_dropdown", "value"),
            prevent_initial_call=True,
        )
        def set_clusters(
            n_clicks, selected_data, n_clusters, features, df, kmeans_col, cluster_id
        ):
            df = pd.read_json(df, orient="split")
            if ctx.triggered_id == "cluster-button":
                kmeans_col = get_kmean(df, int(n_clusters), features)
                style = {"display": "inline"}
                message = "Clusters created!"
                return kmeans_col, style, message
            points = [point["pointIndex"] for point in selected_data[0]["points"]]
            for i in points:
                kmeans_col[i] = cluster_id
            for p in selected_data[0]["points"]:
                kmeans_col[p["customdata"][0]["index"]] = cluster_id
            return kmeans_col, None, None
