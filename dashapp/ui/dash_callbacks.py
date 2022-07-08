import base64
import os

import pandas as pd

from io import BytesIO
from pathlib import Path

from dash import Output, Input, State, ctx, ALL, html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from dashapp.services.dataframe import (
    read_dataframe_with_extension,
    get_data_filepaths,
)
from dashapp.services.dash_layouts import (
    control_data_content,
    control_plots_content,
    control_clusters_content,
)


class Callbacks:
    def __init__(self, plot_types) -> None:
        self.__plot_types = plot_types

    def init_callbacks(self, app, df_from_store, df_to_store):
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
                upload_path = Path("uploads") / Path(status[0]).name

                df = read_dataframe_with_extension(upload_path, upload_path.name)

                upload_path.unlink()

                return (
                    df_to_store(df),
                    generate_dataframe_options(upload_path),
                    str(Path("uploads") / upload_path.name),
                )

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
            def upload(contents, upload_name):
                if contents is None:
                    raise PreventUpdate()

                upload_name = Path(upload_name)
                _content_type, content_string = contents.split(",")
                decoded = base64.b64decode(content_string)

                df = read_dataframe_with_extension(BytesIO(decoded), upload_name)

                if df is None:
                    raise PreventUpdate()
                else:
                    return (
                        df_to_store(df),
                        generate_dataframe_options(upload_name),
                        str(Path("uploads") / upload_name),
                        None,
                        None,
                    )

        @app.callback(
            ServersideOutput("data_frame_store", "data"),
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
            filepath,
        ):
            trigger = ctx.triggered_id

            filepath = Path(filepath)

            if trigger == "submit-button":
                if str(list(filepath.parents)[-2]) == "uploads":
                    df = df_from_store(uploaded_data)
                    df_store = uploaded_data

                    file_message = html.Div(
                        [
                            f"Data file {filepath.name} ",
                            html.I("(upload)"),
                            " loaded successfully!",
                        ]
                    )
                else:
                    filepath = Path("data") / filepath.name

                    df = read_dataframe_with_extension(filepath, filepath.name)
                    df_store = df_to_store(df)

                    file_message = f"Data file {filepath.name} loaded successfully!"
            elif trigger == "uploaded_data_file_store":
                df_store = uploaded_data
                df = df_from_store(uploaded_data)

                file_message = html.Div(
                    [
                        f"Data file {filepath.name} ",
                        html.I("(upload)"),
                        " loaded successfully!",
                    ]
                )

            file_style = {"display": "inline"}
            columns = df.columns.to_list()
            df_store = df_from_store(df_store)
            df_store["auxiliary"] = [{"index": i} for i in range(len(df))]

            return (
                df_to_store(df_store),
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
            df = df_from_store(df)
            # create column for clusters if needed
            if kmeans_col:
                if len(kmeans_col) == df.shape[0]:
                    df["Clusters"] = kmeans_col
            columns = df.columns.to_list()
            layout = self.__plot_types[plot_type].create_new_layout(
                n_clicks, df, columns
            )
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
            df = df_from_store(df)
            if ctx.triggered_id == "cluster-button":
                scaler = StandardScaler()
                scale = scaler.fit_transform(df[features])
                km = KMeans(n_clusters=int(n_clusters)).fit_predict(scale)
                kmeans_col = [f"c{c+1}" for c in km]

                style = {"display": "inline"}
                message = "Clusters created!"
                return kmeans_col, style, message
            if kmeans_col is None:
                kmeans_col = ["bg"] * len(df)
            for p in selected_data[0]["points"]:
                kmeans_col[p["customdata"][0]["index"]] = cluster_id
            return kmeans_col, None, None


def generate_dataframe_options(upload_path):
    return [
        {
            "label": html.Div([upload_path.name, " ", html.I("(upload)")]),
            "value": str(Path("uploads") / upload_path.name),
        }
    ] + [{"label": fp.name, "value": str(fp)} for fp in get_data_filepaths()]
