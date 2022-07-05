import plotly.express as px

from re import sub

from dash import html, dcc
from matplotlib.pyplot import bar

from dashapp.services import dash_layouts


class Scatterplot:
    def __init__(
        self,
        df=None,
        x_axis=None,
        y_axis=None,
        color=None,
        symbol=None,
        clusters=0,
        jitter=0,
        subset_points=None,
    ):
        self.__df = df
        self.__x_axis = x_axis
        self.__y_axis = y_axis
        self.__color = color
        self.__symbol = symbol
        self.__clusters = clusters
        self.__jitter = jitter
        self.__subset_points = subset_points
        self.div_style = {"width": "32%", "display": "inline-block", "float": "left"}
        self.style = {}

    @property
    def inputs(self):
        return {
            "embedding": self.__x_axis.split(" ")[0],
            "color": self.__color,
            "symbol": self.__symbol,
        }

    def set_axes(self, x_axis, y_axis):
        self.__x_axis = x_axis
        self.__y_axis = y_axis

    def set_color(self, variable):
        self.__color = variable

    def set_subset_points(self, subset_points):
        self.__subset_points = subset_points

    def set_symbol(self, variable):
        self.__symbol = variable

    def create_plot(self):
        fig = px.scatter(
            self.__df, self.__x_axis, self.__y_axis, self.__color, self.__symbol
        )
        fig.update_layout(legend=dict(orientation="h", y=-0.15))
        fig.update_layout(coloraxis_colorbar=dict(orientation="h", y=-0.5))
        # fig.update_yaxes(scaleanchor="x", scaleratio=1)
        return fig

    def render(self):
        fig = self.create_plot()
        fig.show()

    def get_layout(self, index, columns):
        layout = html.Div(
            children=[
                dash_layouts.layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_x_axis1", "index": index},
                        options=columns,
                        clearable=False,
                    ),
                    title="x",
                ),
                dash_layouts.layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_y_axis1", "index": index},
                        options=columns,
                        clearable=False,
                    ),
                    title="y",
                ),
                dash_layouts.layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_target_color", "index": index},
                        options=columns,
                    ),
                    title="target (color)",
                ),
                dash_layouts.layout_wrapper(
                    component=dcc.Dropdown(
                        id={"type": "scatter_target_symbol", "index": index},
                        options=columns,
                    ),
                    title="target (symbol)",
                ),
                dash_layouts.layout_wrapper(
                    component=dcc.Slider(
                        id={"type": "jitter-slider", "index": index},
                        min=0,
                        max=1,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                    title="jitter",
                    style={"width": "80%", "padding-left": "2%"},
                ),
                dcc.Graph(
                    id={"type": "scatterplot", "index": index},
                ),
            ],
            id={"type": "scatterplot-container", "index": index},
            style=self.div_style,
        )

        return layout


class Histogram:
    def __init__(
        self,
        df,
        x_axis=None,
        y_axis=None,
        color=None,
        color_dicrete_sequence=None,
        barmode=None,
        subset_points=None,
        title=None,
    ):
        self.__df = df
        self.__x_axis = x_axis
        self.__y_axis = y_axis
        self.__color = color
        self.__color_discrete_sequence = color_dicrete_sequence
        self.__barmode = barmode
        self.__subset_points = subset_points
        self.__title = title
        self.div_style = {"width": "32%", "display": "inline-block", "float": "left"}
        self.style = {"width": "90%", "height": "100%"}

    def set_axes(self, x_axis, y_axis=None):
        self.__x_axis = x_axis
        self.__y_axis = y_axis

    def set_color(self, variable):
        self.__color = variable

    def set_color_discrete_sequence(self, value):
        self.__color_discrete_sequence = value

    def set_subset_points(self, subset_points):
        self.__subset_points = subset_points

    def set_barmode(self, value):
        self.__barmode = value

    def create_plot(self):
        fig = px.histogram(
            self.__df,
            self.__x_axis,
            self.__y_axis,
            self.__color,
            color_discrete_sequence=self.__color_discrete_sequence,
            barmode=self.__barmode,
            title=self.__title,
        )
        return fig

    def add_trace(self, fig, fig_2):
        fig.add_trace(fig_2)

        return fig

    def render(self):
        fig = self.create_plot()
        fig.show()

    def get_layout(self):
        layout = dash_layouts.histogram()
        return layout


class Heatmap:
    def __init__(self, df, x_axis=None, y_axis=None, color=None, title=None) -> None:
        self.__df = df
        self.__x_axis = x_axis
        self.__y_axis = y_axis
        self.__color = color
        self.__title = title

    def set_axes(self, x_axis, y_axis):
        self.__x_axis = x_axis
        self.__y_axis = y_axis

    def set_color(self, variable):
        self.__color = variable

    def create_plot(self):
        fig = px.imshow(
            self.__df,
            x=self.__x_axis,
            y=self.__y_axis,
            color_continuous_scale=self.__color,
            origin="lower",
            title=self.__title,
        )

        return fig

    def render(self):
        fig = self.create_plot()
        fig.show()

    def get_layout(self):
        pass
