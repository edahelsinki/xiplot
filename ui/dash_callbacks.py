from dash import Output, Input, State, ctx
from services.data_frame import read_data_file, get_kmean
from services.graphs import *
from services.dash_layouts import control_data_content, control_scatterplot_content, control_clusters_content
from ui.dash_renderer import render_smiles
import pandas as pd
import numpy as np
import copy


class Callbacks:
    def __init__(self, df=None) -> None:
        self.__df = df

    def get_callbacks(self, app):
        @app.callback(
            Output("control_data_content-container", "style"),
            Output("control_scatter_content-container", "style"),
            Output("control_clusters_content-container", "style"),
            Input("control-tabs", "value"),
        )
        def control(tab):
            style = {"padding-left": "2%"}
            hide_style = {"display": "none"}
            if tab == "control-data-tab":
                return style, hide_style, hide_style
            elif tab == "control-scatterplot-tab":
                return hide_style, style, hide_style
            elif tab == "control-clusters-tab":
                style["padding-top"] = "2%"
                return hide_style, hide_style, style

        @app.callback(
            Output("data_frame_store", "data"),
            Output("data_file_store", "data"),
            Output("data_file_load_message-container", "style"),
            Output("data_file_load_message", "children"),
            Output("scatter_target_color", "options"),
            Output("scatter_target_symbol", "options"),
            Output("x_axis_histo", "options"),
            Output("x_axis_histo", "value"),
            Output("cluster_feature", "options"),
            Output("data_frame_clusters_store", "data"),
            Input("submit-button", "n_clicks"),
            Input("cluster_button", "n_clicks"),
            State("data_files", "value"),
            State("data_frame_clusters_store", "data"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
            State("data_frame_store", "data"),

            prevent_initial_call=True
        )
        def choose_file(data_btn, cluster_btn, filename, clustered_data, n_clusters, features, df):
            trigger = ctx.triggered_id
            if trigger == "submit-button":
                df = read_data_file(filename)
                self.__df = df

                df_store = df.to_json(date_format="iso", orient="split"),
                file_style = {"display": "inline"}
                file_message = f"Data file {filename} loaded successfully!"
                if clustered_data:
                    df = pd.read_json(clustered_data, orient="split")
                columns = df.columns.to_list()
                return df_store, filename, file_style, file_message, columns, columns, columns, columns[0], columns, None
            elif trigger == "cluster_button":
                df = pd.read_json(df[0], orient="split")
                kmean_df = get_kmean(df, int(n_clusters), features)
                columns = kmean_df.columns.to_list()
                self.__df = kmean_df
                kmean_df = kmean_df.to_json(date_format="iso", orient="split")
                return None, None, None, None, columns, columns, columns, columns[0], columns, kmean_df

        @app.callback(
            Output("scatterplot", "figure"),
            Output("scatterplot", "style"),
            Output("scatterplot-container", "style"),
            Output("scatterplot_input_store", "data"),
            Output("jitter-slider", "max"),
            Input("algorythm", "value"),
            Input("scatter_target_color", "value"),
            Input("scatter_target_symbol", "value"),
            Input("jitter-slider", "value"),
            prevent_initial_call=True,
        )
        def render_scatterplot(embedding, target, symbol, jitter):
            x_axis = embedding + " 1"
            y_axis = embedding + " 2"

            jitter_max = (self.__df[x_axis].max()-self.__df[x_axis].min())*0.05

            if jitter:
                jitter = float(jitter)
            df = copy.deepcopy(self.__df)
            if type(jitter) == float:
                if jitter > 0:
                    Z = df[[x_axis, y_axis]].to_numpy("float64")
                    Z = np.random.normal(Z, jitter)
                    jitter_df = pd.DataFrame(Z, columns=[x_axis, y_axis])
                    df[[x_axis, y_axis]] = jitter_df[[x_axis, y_axis]]
            fig = Scatterplot(
                df=df, x_axis=x_axis, y_axis=y_axis, color=target, symbol=symbol)
            return fig.create_plot(), fig.style, fig.div_style, fig.inputs, jitter_max

        @app.callback(
            Output("histogram", "figure"),
            Output("histogram", "style"),
            Output("histogram-container", "style"),
            Output("histo_mean", "children"),
            Output("histo_deviation", "children"),
            Input("x_axis_histo", "value"),
            Input("scatterplot", "selectedData"),
            prevent_initial_call=True,
        )
        def render_histogram(x_axis, slct_data):
            df = copy.deepcopy(self.__df)
            df["Clusters"] = df["Clusters"].astype(float)

            fig = Histogram(df=self.__df, x_axis=x_axis, barmode="overlay")
            style = fig.style
            div_style = fig.div_style

            points = [point["pointIndex"]
                      for point in slct_data["points"]]
            selected_df = df.loc[df.index.isin(points)]
            color = px.colors.qualitative.Dark2
            fig_2 = Histogram(selected_df, x_axis,
                              color_dicrete_sequence=color)
            fig_2 = fig_2.create_plot().data[0]
            fig = fig.add_trace(fig.create_plot(), fig_2)

            mean = round(self.__df[x_axis].mean(), 3)
            deviation = round(self.__df[x_axis].std(), 3)
            selected_mean = round(selected_df[x_axis].mean(), 3)
            selected_deviation = round(selected_df[x_axis].std(), 3)
            return fig, style, div_style, f"Full mean: {mean}, Selected mean: {selected_mean}", f"Full deviation: {deviation}, Selected deviation: {selected_deviation}"
