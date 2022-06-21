from dash import Output, Input, State, html
from services.data_frame import read_data_file, get_kmean
from services.graphs import *
from ui.dash_renderer import render_smiles
import pandas as pd
import numpy as np
import copy


class Callbacks:
    def __init__(self, df=None) -> None:
        self.__df = df

    def get_callbacks(self, app):
        @app.callback(
            Output("x_axis_histo", "options"),
            Output("selected_data_column", "options"),
            Output("scatter_target", "options"),
            Output("x_axis_histo", "value"),
            Output("selected_data_column", "value"),
            Output("scatter_target", "value"),
            Input("submit-button", "n_clicks"),
            State("data_files", "value"),
            prevent_initial_call=True,
        )
        def choose_data_file(n_clicks, filename):
            """
                User chooses a data file to load. Column names are sent to show a histogram and a scatter. 

                Returns:
                    File name as a string and all the columns' names
            """
            self.__df = read_data_file(filename)
            columns = self.__df.columns.tolist()
            return columns, columns, columns, columns[0], columns[0], columns[0]

        @app.callback(
            Output("scatterplot", "figure"),
            Input("algorythm", "value"),
            Input("scatter_target", "value"),
            Input("scatter_cluster", "value"),
            Input("jitter-button", "n_clicks"),
            State("jitter-input", "value"),
            prevent_initial_call=True
        )
        def render_scatter(algorythm, color, n_clusters, n_clicks, jitter):
            """
                Returns a plotly's scatter object with axes given by the user.

                Returns:
                    Scatter object
            """
            x_axis = algorythm + " 1"
            y_axis = algorythm + " 2"
            if jitter is not None:
                try:
                    jitter = float(jitter)
                except ValueError:
                    raise "Invalid input"
            df = copy.deepcopy(self.__df)
            if type(jitter) == float:
                if jitter > 0:
                    Z = df[[x_axis, y_axis]].to_numpy("float64")
                    Z = np.random.normal(Z, jitter)
                    jitter_df = pd.DataFrame(Z, columns=[x_axis, y_axis])
                    df[[x_axis, y_axis]] = jitter_df[[x_axis, y_axis]]

            if n_clusters:
                df = get_kmean(df, int(n_clusters), x_axis, y_axis)
                fig = Scatterplot(df)
                fig.set_symbol("Clusters")
            else:
                fig = Scatterplot(df)
            fig.set_axes(x_axis, y_axis)
            fig.set_color(color)
            fig = fig.create_plot()
            if n_clusters:
                fig.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
            return fig

        @ app.callback(
            Output("histogram", "figure"),
            Output("histo_mean", "children"),
            Output("histo_deviation", "children"),
            Input("x_axis_histo", "value"),
            Input("scatterplot", "selectedData"),
            prevent_initial_call=True,
        )
        def render_histogram(x_axis, selected_data):
            """
                Returns a plotly's histogram object with a x axis given by the user

                Returns:
                    Histogram object
            """
            fig = Histogram(self.__df)
            fig.set_axes(x_axis)

            if selected_data:
                points = [point["pointIndex"]
                          for point in selected_data["points"]]
                selected_df = self.__df.loc[self.__df.index.isin(points)]
                fig_2 = Histogram(selected_df)
                fig_2.set_axes(x_axis)
                fig_2.set_color_discrete_sequence(px.colors.qualitative.Dark2)
                fig_2 = fig_2.create_plot().data[0]
                fig.set_barmode("overlay")
                fig = fig.add_trace(fig.create_plot(), fig_2)

                mean = round(self.__df[x_axis].mean(), 3)
                deviation = round(self.__df[x_axis].std(), 3)
                selected_mean = round(selected_df[x_axis].mean(), 3)
                selected_deviation = round(selected_df[x_axis].std(), 3)
                return fig, f"Full mean: {mean}, Selected mean: {selected_mean}", f"Full deviation: {deviation}, Selected deviation: {selected_deviation}"

            fig = fig.create_plot()
            mean = round(self.__df[x_axis].mean(), 3)
            deviation = round(self.__df[x_axis].std(), 3)
            return fig, f"Mean: {mean}", f"Deviation: {deviation}"

        @app.callback(
            Output("selected", "children"),
            Input("scatterplot", "selectedData"),
            prevent_initial_call=True
        )
        def selected_data(data):
            points = [point["pointIndex"] for point in data["points"]]
            return f"Selected {len(points)} points"

        @app.callback(
            Output("smiles_image", "children"),
            Input("scatterplot", "hoverData"),
            State("data_files", "value"),
            prevent_initial_call=True
        )
        def render_mol_image(hover_data, filename):
            df = read_data_file(filename)
            point = hover_data["points"][0]["pointIndex"]
            try:
                smiles_str = df.loc[point]["SMILES"]
                im = render_smiles(smiles_str)

                children = [
                    html.Img(
                        src=im,
                    ),
                    html.P(smiles_str)
                ]
                return children
            except KeyError:
                return
