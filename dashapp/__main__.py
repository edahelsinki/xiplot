from dashapp.setup import setup_dash_app

app = setup_dash_app(unsafe_local_server=True)

app.run(debug=True)
