from dash import html, dcc
import plotly.express as px
import services.dash_layouts as dash_layouts


class Scatterplot:
    def __init__(self, df):
        self.__df = df
        self.__x_axis = None
        self.__y_axis = None
        self.__color = None
        self.__subset_points = None

    def set_axes(self, x_axis, y_axis):
        self.__x_axis = x_axis
        self.__y_axis = y_axis

    def set_color(self, variable):
        self.__color = variable

    def set_subset_points(self, subset_points):
        self.__subset_points = subset_points

    def render(self):
        fig = px.scatter(self.__df, self.__x_axis, self.__y_axis, self.__color)
        fig.show()

    def get_layout(self):
        layout = dash_layouts.scatterplot()
        return layout


class Histogram:
    def __init__(self, df):
        self.__df = df
        self.__x_axis = None
        self.__y_axis = None
        self.__color = None
        self.__subset_points = None

    def set_axes(self, x_axis, y_axis=None):
        self.__x_axis = x_axis
        self.__y_axis = y_axis

    def set_color(self, variable):
        self.__color = variable

    def set_subset_points(self, subset_points):
        self.__subset_points = subset_points

    def render(self):
        fig = px.histogram(self.__df, self.__x_axis,
                           self.__y_axis, self.__color)
        fig.show()

    def get_layout(self):
        layout = dash_layouts.histogram()
        return layout
