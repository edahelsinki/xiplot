from re import sub
from dash import html, dcc
from matplotlib.pyplot import bar
import plotly.express as px
import services.dash_layouts as dash_layouts


class Scatterplot:
    def __init__(self, df, x_axis=None, y_axis=None, color=None, symbol=None, clusters=0, jitter=0, subset_points=None):
        self.__df = df
        self.__x_axis = x_axis
        self.__y_axis = y_axis
        self.__color = color
        self.__symbol = symbol
        self.__clusters = clusters
        self.__jitter = jitter
        self.__subset_points = subset_points
        self.style = {"width": "65%",
                      "display": "inline-block", "float": "left"}

    @property
    def inputs(self):
        return {"embedding": self.__x_axis.split(" ")[0], "color": self.__color, "symbol": self.__symbol}

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
        fig = px.scatter(self.__df, self.__x_axis,
                         self.__y_axis, self.__color, self.__symbol)
        return fig

    def render(self):
        fig = self.create_plot()
        fig.show()

    def get_layout(self, app):
        layout = dash_layouts.scatterplot()

        """@app.callback(
            Output("scatterplot", "figure"),
            Input("algorythm", "value"),
            Input("scatter_target", "value"),
            Input("scatter_cluster", "value"),
            Input("jitter-button", "n_clicks"),
            State("jitter-input", "value"),
            prevent_initial_call=True
        )
        def render_scatter(algorythm, color, n_clusters, n_clicks, jitter):
            
                Returns a plotly's scatter object with axes given by the user.

                Returns:
                    Scatter object
            
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
            return fig"""
        return layout


class Histogram:
    def __init__(self, df, x_axis=None, y_axis=None, color=None, color_dicrete_sequence=None, barmode=None, subset_points=None):
        self.__df = df
        self.__x_axis = x_axis
        self.__y_axis = y_axis
        self.__color = color
        self.__color_discrete_sequence = color_dicrete_sequence
        self.__barmode = barmode
        self.__subset_points = subset_points
        self.style = {"width": "65%",
                      "display": "inline-block", "float": "left"}

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
        fig = px.histogram(self.__df, self.__x_axis,
                           self.__y_axis, self.__color, color_discrete_sequence=self.__color_discrete_sequence, barmode=self.__barmode)
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
