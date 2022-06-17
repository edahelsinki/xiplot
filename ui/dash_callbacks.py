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
            Output("x_axis", "value"),
            Output("y_axis", "value"),
            Output("x_axis_histo", "value"),
            Output("selected_data_column", "value"),
            Output("selected_histogram_column", "value"),
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
            return columns, columns, columns, columns, columns, columns[0], columns[1], columns[0], columns[0], columns[0]

        @app.callback(
            Output("scatter-plot", "figure"),
            Input("x_axis", "value"), Input("y_axis", "value"),
            prevent_initial_call=True
        )
        def render_scatter(x_axis, y_axis):
            """
                Returns a plotly's scatter object with axes given by the user.

                Returns:
                    Scatter object
            """
            fig = Scatterplot(self.__df)
            fig.set_axes(x_axis, y_axis)
            return fig.create_plot()

        @app.callback(
            Output("histogram", "figure"),
            Output("histo_mean", "children"),
            Output("histo_deviation", "children"),
            Input("x_axis_histo", "value"),
            prevent_initial_call=True,
        )
        def render_histogram(x_axis):
            """
                Returns a plotly's histogram object with a x axis given by the user

                Returns:
                    Histogram object
            """
            fig = Histogram(self.__df)
            fig.set_axes(x_axis)
            mean = self.__df[x_axis].mean()
            deviation = self.__df[x_axis].std()
            return fig.create_plot(), f"Mean: {mean}", f"Deviation: {deviation}"

        @app.callback(
            Output("selected", "children"),
            Input("scatter-plot", "selectedData"),
            prevent_initial_call=True
        )
        def selected_data(data):
            points = [point["pointIndex"] for point in data["points"]]
            return f"Selected {len(points)} points"

        @app.callback(
            Output("selected_histogram", "figure"),
            Output("selected_mean", "children"),
            Output("selected_deviation", "children"),
            Input("scatter-plot", "selectedData"),
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
            Input("scatter-plot", "hoverData"),
            State("data_files", "value"),
            prevent_initial_call=True
        )
        def render_mol_image(hover_data, filename):
            df = read_data_file(filename)
            point = hover_data["points"][0]["pointIndex"]
            smiles_str = df.loc[point]["SMILES"]
            im = render_smiles(smiles_str)

            children = [
                html.Img(
                    src=im,
                ),
                html.P(smiles_str)
            ]
            return children
