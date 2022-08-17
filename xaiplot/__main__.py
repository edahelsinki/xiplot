from xaiplot.setup import setup_xaiplot_dash_app

app = setup_xaiplot_dash_app(unsafe_local_server=True)

app.run(debug=True)
