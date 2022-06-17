from re import sub
from dash import html, dcc
import plotly.express as px
import services.dash_layouts as dash_layouts


class Scatterplot:
    def __init__(self, df, x_axis=None, y_axis=None, color=None, subset_points=None):
        self.__df = df
        self.__x_axis = x_axis
        self.__y_axis = y_axis
        self.__color = color
        self.__subset_points = subset_points

    def set_axes(self, x_axis, y_axis):
        self.__x_axis = x_axis
        self.__y_axis = y_axis

    def set_color(self, variable):
        self.__color = variable

    def set_subset_points(self, subset_points):
        self.__subset_points = subset_points

    def create_plot(self):
        fig = px.scatter(self.__df, self.__x_axis, self.__y_axis, self.__color)
        return fig

    def render(self):
        fig = self.create_plot()
        fig.show()

    def get_layout(self):
        layout = dash_layouts.scatterplot()
        return layout


class Histogram:
    def __init__(self, df, x_axis=None, y_axis=None, color=None, color_dicrete_sequence=None, subset_points=None):
        self.__df = df
        self.__x_axis = x_axis
        self.__y_axis = y_axis
        self.__color = color
        self.__color_discrete_sequence = color_dicrete_sequence
        self.__subset_points = subset_points

    def set_axes(self, x_axis, y_axis=None):
        self.__x_axis = x_axis
        self.__y_axis = y_axis

    def set_color(self, variable):
        self.__color = variable

    def set_subset_points(self, subset_points):
        self.__subset_points = subset_points

    def create_plot(self):
        fig = px.histogram(self.__df, self.__x_axis,
                           self.__y_axis, self.__color, color_discrete_sequence=self.__color_discrete_sequence)
        return fig

    def add_trace(self, fig, fig_2):
        fig.add_trace(fig_2)

    def render(self):
        fig = self.create_plot()
        fig.show()

    def get_layout(self):
        layout = dash_layouts.histogram()
        return layout
