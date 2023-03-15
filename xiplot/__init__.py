def cli():
    from xiplot.setup import setup_xiplot_dash_app

    app = setup_xiplot_dash_app(unsafe_local_server=True)
    app.run(debug=True)
