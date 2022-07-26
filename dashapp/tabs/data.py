import base64
import os

import dash
import pandas as pd
import plotly.express as px

from io import BytesIO
from pathlib import Path

from dash import Output, Input, State, ctx, html, dcc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput

from dashapp.utils.dataframe import (
    read_dataframe_with_extension,
    get_data_filepaths,
)
from dashapp.tabs import Tab
from dashapp.utils.layouts import layout_wrapper


class Data(Tab):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        try:
            import dash_uploader as du

            @du.callback(
                output=[
                    ServersideOutput("uploaded_data_file_store", "data"),
                    Output("data_files", "options"),
                    Output("data_files", "value"),
                ],
                id="file_uploader",
            )
            def upload(status):
                upload_path = Path("uploads") / Path(status[0]).name

                df = read_dataframe_with_extension(upload_path, upload_path.name)

                upload_path.unlink()

                return (
                    df_to_store(df),
                    generate_dataframe_options(upload_path),
                    str(Path("uploads") / upload_path.name),
                )

        except ImportError:

            @app.callback(
                ServersideOutput("uploaded_data_file_store", "data"),
                Output("data_files", "options"),
                Output("data_files", "value"),
                Output("file_uploader", "contents"),
                Output("file_uploader", "filename"),
                Input("file_uploader", "contents"),
                State("file_uploader", "filename"),
            )
            def upload(contents, upload_name):
                if contents is None:
                    raise PreventUpdate()

                upload_name = Path(upload_name)
                _content_type, content_string = contents.split(",")
                decoded = base64.b64decode(content_string)

                df = read_dataframe_with_extension(BytesIO(decoded), upload_name)

                if df is None:
                    raise PreventUpdate()
                else:
                    return (
                        df_to_store(df),
                        generate_dataframe_options(upload_name),
                        str(Path("uploads") / upload_name),
                        None,
                        None,
                    )

        @app.callback(
            ServersideOutput("data_frame_store", "data"),
            Input("submit-button", "n_clicks"),
            Input("uploaded_data_file_store", "data"),
            State("data_files", "value"),
            prevent_initial_call=True,
            log=True,
        )
        def choose_file(
            data_btn,
            uploaded_data,
            filepath,
            dash_logger,
        ):
            trigger = ctx.triggered_id

            if not filepath:
                dash_logger.warning(
                    message="You have not selected a data file to load.",
                    autoClose=10000,
                )

                return dash.no_update

            filepath = Path(filepath)

            if trigger == "submit-button":
                if str(list(filepath.parents)[-2]) == "uploads":
                    df = df_from_store(uploaded_data)
                    df_store = uploaded_data

                    dash_logger.info(
                        color="green",
                        title="Success",
                        message=[
                            html.Div(
                                [
                                    f"The data file {filepath.name} ",
                                    html.I("(upload)"),
                                    " was loaded successfully!",
                                ]
                            )
                        ],
                        autoClose=5000,
                    )
                else:
                    filepath = Path("data") / filepath.name

                    df = read_dataframe_with_extension(filepath, filepath.name)
                    df_store = df_to_store(df)

                    dash_logger.info(
                        color="green",
                        title="Success",
                        message=f"The data file {filepath.name} was loaded successfully!",
                        autoClose=5000,
                    )
            elif trigger == "uploaded_data_file_store":
                df_store = uploaded_data
                df = df_from_store(uploaded_data)

                dash_logger.info(
                    color="green",
                    title="Success",
                    message=[
                        html.Div(
                            [
                                f"The data file {filepath.name} ",
                                html.I("(upload)"),
                                " was uploaded successfully!",
                            ]
                        )
                    ],
                    autoClose=5000,
                )

            df_store = df_from_store(df_store)
            df_store["auxiliary"] = [{"index": i} for i in range(len(df))]

            return df_to_store(df_store)

    @staticmethod
    def create_layout():
        try:
            import dash_uploader as du

            uploader = du.Upload(
                id="file_uploader",
                text="Drag and Drop or Select a File to upload",
                default_style={"minHeight": 1, "lineHeight": 4, "height": "85px"},
            )
        except ImportError:
            uploader = dcc.Upload(
                id="file_uploader",
                children=html.Div(
                    [
                        "Drag and Drop or ",
                        html.A("Select a File"),
                        " to upload",
                    ]
                ),
                className="dcc-upload",
            )

        return html.Div(
            [
                html.Div(
                    [
                        layout_wrapper(
                            component=dcc.Dropdown(
                                [
                                    {"label": fp.name, "value": str(fp)}
                                    for fp in get_data_filepaths()
                                ],
                                id="data_files",
                            ),
                            title="Choose a data file",
                            style={"margin-left": "5%", "width": "100%"},
                        ),
                        html.Div(
                            [
                                html.Button(
                                    "Load the data file",
                                    id="submit-button",
                                    n_clicks=0,
                                    className="btn btn-primary",
                                ),
                            ],
                            style={"margin-top": "1%", "margin-left": "5%"},
                        ),
                    ],
                    style={"float": "left", "width": "40%"},
                ),
                html.Div([uploader], className="dash-uploader"),
            ],
            id="control_data_content-container",
        )


def generate_dataframe_options(upload_path):
    return [
        {
            "label": html.Div([upload_path.name, " ", html.I("(upload)")]),
            "value": str(Path("uploads") / upload_path.name),
        }
    ] + [{"label": fp.name, "value": str(fp)} for fp in get_data_filepaths()]
