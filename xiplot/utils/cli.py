def cli():
    from xiplot.setup import setup_xiplot_dash_app
    import argparse
    import os

    parser = argparse.ArgumentParser(
        prog="xiplot",
        description="Xiplot:   A Dash app for interactively visualising data",
    )
    parser.add_argument(
        "PATH",
        nargs="?",
        default="data",
        help="The path to a directory containing data files",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-p", "--port", help="Port used to serve the application")
    parser.add_argument("--host", help="Host IP used to serve the application")
    parser.add_argument(
        "-s",
        "--serversideoutput",
        action="store_true",
        help="Use ServersideOutput component to keep the data on the server",
    )
    args = parser.parse_args()
    path = args.PATH

    # TODO: How to add this path to utils.dataframe.get_data_filepaths

    if not os.path.isdir(path):
        print(f'Directory "{path}" was not found')

    kwargs = {}
    if args.debug:
        kwargs["debug"] = True
    if args.host:
        kwargs["host"] = args.host
    if args.port:
        kwargs["port"] = args.port

    # TODO: Is there a better solution for this?
    unsafe_local_server = True if args.serversideoutput else False

    app = setup_xiplot_dash_app(unsafe_local_server=unsafe_local_server)
    app.run(**kwargs)
