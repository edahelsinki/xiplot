def cli():
    import argparse
    import os

    from xiplot.setup import setup_xiplot_dash_app

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
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug mode"
    )
    parser.add_argument(
        "-p", "--port", help="Port used to serve the application"
    )
    parser.add_argument("--host", help="Host IP used to serve the application")
    parser.add_argument(
        "-c",
        "--cache",
        action="store_true",
        help=(
            "Cache datasets on the server in order to reduce the amount of"
            " data transferred. Might not be suitable for servers with"
            " multiple users"
        ),
    )
    parser.add_argument(
        "--plugin", help="The path to a directory containing plugin .whl files"
    )
    args = parser.parse_args()
    path = args.PATH

    if not os.path.isdir(path):
        print(f'Directory "{path}" was not found')

    kwargs = {}
    if args.debug:
        kwargs["debug"] = True
    if args.host:
        kwargs["host"] = args.host
    if args.port:
        kwargs["port"] = args.port
    if args.plugin:
        plugin_dir = args.plugin
    else:
        plugin_dir = "plugins"

    unsafe_local_server = True if args.cache else False

    app = setup_xiplot_dash_app(
        unsafe_local_server=unsafe_local_server,
        data_dir=path,
        plugin_dir=plugin_dir,
    )
    app.run(**kwargs)
