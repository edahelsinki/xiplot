from dash import Output, Input, State, html
from services.data_frame import read_data_file
from services.graphs import *
from ui.dash_renderer import render_smiles
import pandas as pd
import numpy as np


class Callbacks:
    def __init__(self, df=None) -> None:
        self.__df = df

    def get_callbacks(self, app):
        @app.callback(
            Output("x_axis", "options"),
            Output("y_axis", "options"),
            Output("x_axis_histo", "options"),
            Output("selected_data_column", "options"),
            Output("selected_histogram_column", "options"),
            Output("scatter_target", "options"),
            Output("x_axis", "value"),
            Output("y_axis", "value"),
            Output("x_axis_histo", "value"),
            Output("selected_data_column", "value"),
            Output("selected_histogram_column", "value"),
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
            return columns, columns, columns, columns, columns, columns, columns[0], columns[1], columns[0], columns[0], columns[0], columns[0]

        @app.callback(
            Output("scatterplot", "figure"),
            Input("x_axis", "value"), Input("y_axis", "value"),
            Input("scatter_target", "value"),
            prevent_initial_call=True
        )
        def render_scatter(x_axis, y_axis, color):
            """
                Returns a plotly's scatter object with axes given by the user.

                Returns:
                    Scatter object
            """
            fig = Scatterplot(self.__df, color=color)
            fig.set_axes(x_axis, y_axis)
            return fig.create_plot()

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

            else:
                fig = fig.create_plot()
            mean = self.__df[x_axis].mean()
            deviation = self.__df[x_axis].std()
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
            Output("selected_histogram", "figure"),
            Output("selected_mean", "children"),
            Output("selected_deviation", "children"),
            Input("scatterplot", "selectedData"),
            Input("selected_histogram_column", "value"),
            State("data_files", "value"),
            prevent_initial_call=True
        )
        def render_histogram_by_selected_points(data, x_axis, filename):
            points = [point["pointIndex"] for point in data["points"]]
            selected_df = self.__df.loc[self.__df.index.isin(points)]
            fig = Histogram(selected_df)
            fig.set_axes(x_axis)
            mean = selected_df[x_axis].mean()
            deviation = selected_df[x_axis].std()
            return fig.create_plot(), f"Mean: {mean}", f"Deviation: {deviation}"

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
