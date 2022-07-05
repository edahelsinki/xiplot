import base64
import copy
import os

import pandas as pd
import numpy as np

from io import BytesIO

from dash import Output, Input, State, ctx
from dash.exceptions import PreventUpdate

from dashapp.services.data_frame import (
    read_data_file,
    read_dataframe_with_extension,
    get_kmean,
    get_data_files,
)
from dashapp.services.graphs import *
from dashapp.services.dash_layouts import (
    control_data_content,
    control_scatterplot_content,
    control_clusters_content,
)
from dashapp.ui.dash_renderer import render_smiles


class Callbacks:
    def init_callbacks(self, app):
        @app.callback(
            Output("control_data_content-container", "style"),
            Output("control_scatter_content-container", "style"),
            Output("control_plots_content-container", "style"),
            Output("control_clusters_content-container", "style"),
            Input("control-tabs", "value"),
        )
        def control(tab):
            style = {"padding-left": "2%"}
            hide_style = {"display": "none"}
            if tab == "control-data-tab":
                return style, hide_style, hide_style, hide_style
            elif tab == "control-scatterplot-tab":
                return hide_style, style, hide_style, hide_style
            elif tab == "control-plots-tab":
                return hide_style, hide_style, style, hide_style
            elif tab == "control-clusters-tab":
                style["padding-top"] = "2%"
                return hide_style, hide_style, hide_style, style

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
            Output("scatter_x_axis", "options"),
            Output("scatter_x_axis", "value"),
            Output("scatter_y_axis", "options"),
            Output("scatter_y_axis", "value"),
            Output("scatter_target_color", "options"),
            Output("scatter_target_symbol", "options"),
            Output("x_axis_histo", "options"),
            Output("x_axis_histo", "value"),
            Output("cluster_feature", "options"),
            Output("clusters_column_store", "data"),
            Input("submit-button", "n_clicks"),
            Input("cluster_button", "n_clicks"),
            Input("uploaded_data_file_store", "data"),
            State("data_files", "value"),
            State("scatter_x_axis", "value"),
            State("scatter_y_axis", "value"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
            State("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def choose_file(
            data_btn,
            cluster_btn,
            uploaded_data,
            filename,
            x_axis,
            y_axis,
            n_clusters,
            features,
            df,
        ):
            trigger = ctx.triggered_id
            if trigger == "cluster_button" and n_clusters and features:
                df_store = df
                df = pd.read_json(df, orient="split")
                kmeans_col = get_kmean(df, int(n_clusters), features)
                df["Clusters"] = kmeans_col
                columns = df.columns.to_list()

                return (
                    df_store,
                    None,
                    None,
                    None,
                    columns,
                    x_axis,
                    columns,
                    y_axis,
                    columns,
                    columns,
                    columns,
                    columns[0],
                    columns,
                    kmeans_col,
                )
            elif trigger == "submit-button":
                if len(filename.split(" ")) < 2:
                    df = read_data_file(filename)
                    df_store = df.to_json(date_format="iso", orient="split")
                elif filename.endswith(" (Uploaded)"):
                    df = pd.read_json(uploaded_data, orient="split")
                    df_store = uploaded_data
                else:
                    return
                file_message = f"Data file {filename} loaded successfully!"
            elif trigger == "uploaded_data_file_store":
                df_store = uploaded_data
                df = pd.read_json(uploaded_data, orient="split")
                filename = filename[:-11]
                file_message = f"Data file {filename} loaded successfully!"

            columns = df.columns.to_list()
            scatter_x = ""
            scatter_y = ""
            for column in columns:
                if type(column) != str:
                    break
                if "x-" in column or " 1" in column:
                    scatter_x = column
                elif "y-" in column or " 2" in column:
                    scatter_y = column
                    break
            file_style = {"display": "inline"}
            submit_btn = trigger == "submit-button"
            return (
                df_store,
                filename if submit_btn else None,
                file_style,
                file_message,
                columns,
                scatter_x,
                columns,
                scatter_y,
                columns,
                columns,
                columns,
                columns[0],
                columns,
                None,
            )

        @app.callback(
            Output("scatterplot", "figure"),
            Output("scatterplot", "style"),
            Output("scatterplot-container", "style"),
            Output("jitter-slider", "max"),
            Input("scatter_x_axis", "value"),
            Input("scatter_y_axis", "value"),
            Input("scatter_target_color", "value"),
            Input("scatter_target_symbol", "value"),
            Input("jitter-slider", "value"),
            Input("clusters_column_store", "data"),
            Input("data_frame_store", "data"),
            prevent_initial_call=True,
        )
        def render_scatterplot(x_axis, y_axis, color, symbol, jitter, kmeans_col, df):
            df = pd.read_json(df, orient="split")
            if kmeans_col:
                df["Clusters"] = kmeans_col
                # Make color scale discrete
                df["Clusters"] = df["Clusters"].astype(str)
            if type(df[x_axis]) == float:
                jitter_max = (df[x_axis].max() - df[x_axis].min()) * 0.05
            else:
                jitter_max = None

            if jitter:
                jitter = float(jitter)
            if type(jitter) == float:
                if jitter > 0:
                    Z = df[[x_axis, y_axis]].to_numpy("float64")
                    Z = np.random.normal(Z, jitter)
                    jitter_df = pd.DataFrame(Z, columns=[x_axis, y_axis])
                    df[[x_axis, y_axis]] = jitter_df[[x_axis, y_axis]]
            fig = Scatterplot(
                df=df, x_axis=x_axis, y_axis=y_axis, color=color, symbol=symbol
            )
            return fig.create_plot(), fig.style, fig.div_style, jitter_max

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
