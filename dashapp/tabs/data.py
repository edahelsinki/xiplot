import base64
import os
import uuid

import pandas as pd
import dash
import dash_mantine_components as dmc

from io import BytesIO
from pathlib import Path

from dash import Output, Input, State, ctx, html, dcc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput

from dashapp.utils.dataframe import (
    read_dataframe_with_extension,
    get_data_filepaths,
    write_only_dataframe,
    write_dataframe_and_metadata,
)
from dashapp.tabs import Tab
from dashapp.utils.layouts import layout_wrapper
from dashapp.utils.cluster import cluster_colours


class Data(Tab):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        try:
            import dash_uploader as du

            @du.callback(
                output=[
                    ServersideOutput("uploaded_data_file_store", "data"),
                    ServersideOutput("uploaded_auxiliary_store", "data"),
                    Output("uploaded_metadata_store", "data"),
                    Output("data_files", "options"),
                    Output("data_files", "value"),
                    Output("file_uploader_container", "children"),
                    Output("data-tab-upload-notify-container", "children"),
                ],
                id="file_uploader",
            )
            def upload(status):
                upload_path = Path("uploads") / Path(status[0]).name

                uploader = du.Upload(
                    id="file_uploader",
                    text="Drag and Drop or Select a File to upload",
                    default_style={"minHeight": 1, "lineHeight": 4, "height": "85px"},
                )

                try:
                    df, aux, meta = read_dataframe_with_extension(
                        upload_path, upload_path.name
                    )
                except Exception as err:
                    return (
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        [uploader],
                        dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="yellow",
                            title="Warning",
                            message=[
                                html.Div(
                                    [
                                        f"The file {upload_path.name} ",
                                        html.I("(upload)"),
                                        f" could not be loaded as a data frame: {err}.",
                                    ]
                                )
                            ],
                            action="show",
                            autoClose=10000,
                        ),
                    )
                finally:
                    upload_path.unlink()

                return (
                    df_to_store(df),
                    df_to_store(aux),
                    meta,
                    generate_dataframe_options(upload_path),
                    str(Path("uploads") / upload_path.name),
                    [uploader],
                    None,
                )

        except ImportError:

            @app.callback(
                ServersideOutput("uploaded_data_file_store", "data"),
                ServersideOutput("uploaded_auxiliary_store", "data"),
                Output("uploaded_metadata_store", "data"),
                Output("data_files", "options"),
                Output("data_files", "value"),
                Output("file_uploader", "contents"),
                Output("file_uploader", "filename"),
                Output("data-tab-upload-notify-container", "children"),
                Input("file_uploader", "contents"),
                State("file_uploader", "filename"),
            )
            def upload(contents, upload_name):
                if contents is None:
                    raise PreventUpdate()

                upload_name = Path(upload_name)
                _content_type, content_string = contents.split(",")
                decoded = base64.b64decode(content_string)

                try:
                    df, aux, meta = read_dataframe_with_extension(
                        BytesIO(decoded), upload_name
                    )
                except Exception as err:
                    return (
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        None,
                        None,
                        dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="yellow",
                            title="Warning",
                            message=[
                                html.Div(
                                    [
                                        f"The file {upload_name} ",
                                        html.I("(upload)"),
                                        f" could not be loaded as a data frame: {err}.",
                                    ]
                                )
                            ],
                            action="show",
                            autoClose=10000,
                        ),
                    )

                return (
                    df_to_store(df),
                    df_to_store(aux),
                    meta,
                    generate_dataframe_options(upload_name),
                    str(Path("uploads") / upload_name.name),
                    None,
                    None,
                    None,
                )

        @app.callback(
            Output("metadata_session", "data"),
            Input("will-never-be-called", "data"),
        )
        def delay_metadata_session_update(never):
            return dash.no_update

        @app.callback(
            ServersideOutput("data_frame_store", "data"),
            Output("metadata_store", "data"),
            Output("metadata_session", "data"),
            Output("clusters_column_store", "data"),
            Output("selected_rows_store", "data"),
            Output("clusters_column_store_reset", "children"),
            Output("data-tab-notify-container", "children"),
            Input("submit-button", "n_clicks"),
            Input("uploaded_data_file_store", "data"),
            Input("uploaded_auxiliary_store", "data"),
            Input("uploaded_metadata_store", "data"),
            State("data_files", "value"),
        )
        def choose_file(
            data_btn,
            uploaded_data,
            uploaded_aux,
            uploaded_meta,
            filepath,
        ):
            trigger = ctx.triggered_id

            if not filepath:
                return (
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message="You have not selected a data file to load.",
                        action="show",
                        autoClose=10000,
                    ),
                )

            filepath = Path(filepath)

            notification = None

            if trigger == "submit-button":
                if str(list(filepath.parents)[-2]) == "uploads":
                    df_store = uploaded_data
                    aux = df_from_store(uploaded_aux)
                    meta = uploaded_meta

                    notification = dmc.Notification(
                        id=str(uuid.uuid4()),
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
                        action="show",
                        autoClose=5000,
                    )
                else:
                    filepath = Path("data") / filepath.name

                    try:
                        df, aux, meta = read_dataframe_with_extension(
                            filepath, filepath.name
                        )
                    except Exception as err:
                        return (
                            dash.no_update,
                            dash.no_update,
                            dash.no_update,
                            dash.no_update,
                            dash.no_update,
                            dash.no_update,
                            dmc.Notification(
                                id=str(uuid.uuid4()),
                                color="yellow",
                                title="Warning",
                                message=f"The file {filepath.name} could not be loaded as a data frame: {err}.",
                                action="show",
                                autoClose=10000,
                            ),
                        )

                    df_store = df_to_store(df)

                    notification = dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="green",
                        title="Success",
                        message=f"The data file {meta['filename']} was loaded successfully!",
                        action="show",
                        autoClose=5000,
                    )
            elif trigger == "uploaded_data_file_store":
                df_store = uploaded_data
                aux = df_from_store(uploaded_aux)
                meta = uploaded_meta

                notification = dmc.Notification(
                    id=str(uuid.uuid4()),
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
                    action="show",
                    autoClose=5000,
                )

            if meta.get("settings") is None:
                meta["settings"] = dict()

            if meta.get("plots") is None:
                meta["plots"] = dict()

            df = df_from_store(df_store)

            if "is_selected" in aux:
                if aux.dtypes["is_selected"] != bool:
                    return (
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="yellow",
                            title="Warning",
                            message=f'The file {filepath.name} could not be loaded as a data frame: auxiliary column "is_selected" is not of type bool.',
                            action="show",
                            autoClose=10000,
                        ),
                    )

                selected_rows = list(~aux["is_selected"].values)
            else:
                selected_rows = [True] * df.shape[0]

            if "cluster" in aux:
                clusters = list(aux["cluster"].values)

                invalid_clusters = set(clusters) - set(cluster_colours().keys())

                if len(invalid_clusters) > 0:
                    return (
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="yellow",
                            title="Warning",
                            message=f'The file {filepath.name} could not be loaded as a data frame: auxiliary column "cluster" contains invalid values {invalid_clusters}.',
                            action="show",
                            autoClose=10000,
                        ),
                    )
            else:
                clusters = ["all"] * df.shape[0]

            return (
                df_store,
                meta,
                str(uuid.uuid4()),
                clusters,
                selected_rows,
                str(uuid.uuid4()),
                notification,
            )

        @app.callback(
            Output("data-download", "data"),
            Output("data-tab-download-notify-container", "children"),
            Input("download-data-file-button", "n_clicks"),
            Input("download-plots-file-button", "n_clicks"),
            State("data_files", "value"),
            State("data_frame_store", "data"),
            State("metadata_store", "data"),
            State("clusters_column_store", "data"),
            State("selected_rows_store", "data"),
            prevent_initial_call=True,
        )
        def download_file(
            d_clicks,
            p_clicks,
            filepath,
            df,
            meta,
            clusters,
            selected_rows,
        ):
            df = df_from_store(df)

            if filepath is None or df is None:
                return dash.no_update, dmc.Notification(
                    id=str(uuid.uuid4()),
                    color="yellow",
                    title="Warning",
                    message="You have not yet loaded any data file.",
                    action="show",
                    autoClose=10000,
                )

            filepath = Path(filepath)

            file = BytesIO()

            if ctx.triggered_id == "download-data-file-button":
                try:
                    filename, mime = write_only_dataframe(df, meta["filename"], file)
                except Exception as err:
                    return dash.no_update, dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=[
                            html.Div(
                                [
                                    f"Failed to download the data file for {filepath.name}",
                                    html.I(" (upload)")
                                    if ctx.triggered_id == "uploaded_data_file_store"
                                    else None,
                                    f": {err}.",
                                ]
                            )
                        ],
                        action="show",
                        autoClose=10000,
                    )

            if ctx.triggered_id == "download-plots-file-button":
                try:
                    aux = dict()

                    if clusters is not None:
                        aux["cluster"] = clusters

                    if selected_rows is not None:
                        aux["is_selected"] = [not s for s in selected_rows]

                    filename, mime = write_dataframe_and_metadata(
                        df, pd.DataFrame(aux), meta, meta["filename"], file
                    )
                except Exception as err:
                    return dash.no_update, dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=[
                            html.Div(
                                [
                                    f"Failed to download plots and data file for {filepath.name}",
                                    html.I(" (upload)")
                                    if ctx.triggered_id == "uploaded_data_file_store"
                                    else None,
                                    f": {err}.",
                                ]
                            )
                        ],
                        action="show",
                        autoClose=10000,
                    )

            encoded = base64.b64encode(file.getvalue()).decode("ascii")

            return (
                dict(base64=True, content=encoded, filename=filename, type=mime),
                None,
            )

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
                                    style={
                                        "margin-left": "auto",
                                        "margin-right": "auto",
                                    },
                                ),
                                html.Button(
                                    "Download only the data file",
                                    id="download-data-file-button",
                                    n_clicks=0,
                                    className="btn btn-primary",
                                    style={
                                        "margin-left": "auto",
                                        "margin-right": "auto",
                                    },
                                ),
                                html.Button(
                                    "Download the combined plots-and-data file",
                                    id="download-plots-file-button",
                                    n_clicks=0,
                                    className="btn btn-primary",
                                    style={
                                        "margin-left": "auto",
                                        "margin-right": "auto",
                                    },
                                ),
                                dcc.Download(
                                    id="data-download",
                                ),
                            ],
                            style={
                                "margin-top": "1%",
                                "margin-left": "5%",
                                "display": "flex",
                            },
                        ),
                    ],
                    style={"float": "left", "width": "40%"},
                ),
                html.Div(
                    [uploader], id="file_uploader_container", className="dash-uploader"
                ),
            ],
            id="control_data_content-container",
        )

    @staticmethod
    def create_layout_globals():
        return html.Div(
            [
                dcc.Store(id="uploaded_data_file_store"),
                dcc.Store(id="uploaded_auxiliary_store"),
                dcc.Store(id="uploaded_metadata_store"),
                dcc.Store(id="metadata_session"),
                html.Div(id="data-tab-notify-container", style={"display": "none"}),
                html.Div(
                    id="data-tab-upload-notify-container", style={"display": "none"}
                ),
                html.Div(
                    id="data-tab-download-notify-container", style={"display": "none"}
                ),
            ]
        )


def generate_dataframe_options(upload_path):
    return [
        {
            "label": html.Div([upload_path.name, " ", html.I("(upload)")]),
            "value": str(Path("uploads") / upload_path.name),
        }
    ] + [{"label": fp.name, "value": str(fp)} for fp in get_data_filepaths()]
