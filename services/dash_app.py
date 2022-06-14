from dash import Dash, html


app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children="Hello World!")
])


def start():
    app.run_server()
