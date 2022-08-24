from xiplot.setup import setup_xiplot_dash_app

if __name__ == "__main__":
  app = setup_xiplot_dash_app(unsafe_local_server=True)
  app.run(debug=True)
