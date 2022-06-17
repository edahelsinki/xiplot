from dash import html, dcc
import plotly.express as px


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
        layout = html.Div([
            html.Div([
                html.Div([
                    html.H5(children="x axis (scatter)"),
                ], style={"padding-top": 8}),
                dcc.Dropdown(id="x_axis", clearable=False), ],
                style={"width": "40%", "display": "inline-block",
                       "margin-left": "10%"}
            ),
            html.Div([
                html.Div([
                    html.H5(children="y axis (scatter)"),
                ], style={"padding-top": 8}),
                dcc.Dropdown(id="y_axis", clearable=False), ],
                style={"width": "40%", "display": "inline-block", "margin": 10}
            ),
            dcc.Graph(id="scatter-plot"),
        ], style={"width": "33%", "display": "inline-block", "float": "left"})

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
