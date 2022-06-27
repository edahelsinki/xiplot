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
            Output("control-tabs-content", "children"),
            Input("control-tabs", "value"),
            State("data_file_store", "data"),
            State("scatterplot_store", "data"),
        )
        def control(tab, filename, user_inputs):
            if tab == "control-data-tab":
                return control_data_content(filename)
            elif tab == "control-scatterplot-tab":
                return control_scatterplot_content(user_inputs)
            elif tab == "control-clusters-tab":
                return control_clusters_content()

        @app.callback(
            Output("data_frame_store", "data"),
            Output("data_file_store", "data"),
            Output("data_file_load_message-container", "style"),
            Output("data_file_load_message", "children"),
            Input("submit-button", "n_clicks"),
            State("data_files", "value"),
            prevent_initial_call=True
        )
        def choose_file(n_clicks, filename):
            print(ctx.triggered_id)
            self.__df = read_data_file(filename)
            file_style = {"display": "inline"}
            file_message = f"Data file {filename} loaded successfully!"
            return self.__df.to_json(date_format="iso", orient="split"), filename, file_style, file_message

        @app.callback(
            Output("scatter_target", "options"),
            Output("scatter_target_symbol", "options"),
            Output("x_axis_histo", "options"),
            Output("x_axis_histo", "value"),
            Input("control-tabs", "value"),
            State("data_frame_store", "data"),
        )
        def target(tab, data):
            df = pd.read_json(data, orient="split")
            columns = df.columns.to_list()
            return columns, columns, columns, columns[0]

        @app.callback(
            Output("cluster_feature", "options"),
            Input("control-tabs", "value"),
            State("data_frame_store", "data")
        )
        def cluster_feature(tab, data):
            df = pd.read_json(data, orient="split")
            columns = df.columns.to_list()
            return columns

        @app.callback(
            Output("scatterplot", "figure"),
            Output("scatterplot-container", "style"),
            Output("scatterplot_store", "data"),
            Output("jitter-slider", "max"),
            Input("algorythm", "value"),
            Input("scatter_target", "value"),
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
            return fig.create_plot(), fig.style, fig.inputs, jitter_max

        @app.callback(
            Output("histogram", "figure"),
            Output("histo_mean", "children"),
            Output("histo_deviation", "children"),
            Output("histogram-container", "style"),
            Input("x_axis_histo", "value"),
            Input("scatterplot", "selectedData"),
            prevent_initial_call=True,
        )
        def render_histogram(x_axis, slct_data):
            fig = Histogram(df=self.__df, x_axis=x_axis, barmode="overlay")
            style = fig.style

            points = [point["pointIndex"]
                      for point in slct_data["points"]]
            selected_df = self.__df.loc[self.__df.index.isin(points)]
            color = px.colors.qualitative.Dark2
            fig_2 = Histogram(selected_df, x_axis,
                              color_dicrete_sequence=color)
            fig_2 = fig_2.create_plot().data[0]
            fig = fig.add_trace(fig.create_plot(), fig_2)

            mean = round(self.__df[x_axis].mean(), 3)
            deviation = round(self.__df[x_axis].std(), 3)
            selected_mean = round(selected_df[x_axis].mean(), 3)
            selected_deviation = round(selected_df[x_axis].std(), 3)
            return fig, f"Full mean: {mean}, Selected mean: {selected_mean}", f"Full deviation: {deviation}, Selected deviation: {selected_deviation}", style

        """@app.callback(
            Output("data_frame_store", "data"),
            Input("cluster_button", "n_clicks"),
            State("cluster_amount", "value"),
            State("cluster_feature", "value"),
            State("data_frame_store", "data"),
        )
        def compute_clusters(n_clicks, n_clusters, features, df):
            kmean_df = get_kmean(df, int(n_clusters), features)
            print(kmean_df)
            return kmean_df"""
