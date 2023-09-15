import base64
import uuid
from collections import OrderedDict
from io import BytesIO
from pathlib import Path

import dash
import dash_mantine_components as dmc
from dash import ALL, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput

from xiplot.tabs import Tab
from xiplot.utils import generate_id
from xiplot.utils.auxiliary import (
    CLUSTER_COLUMN_NAME,
    SELECTED_COLUMN_NAME,
    decode_aux,
    encode_aux,
    get_clusters,
)
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.components import FlexRow, PlotData
from xiplot.utils.dataframe import (
    get_data_filepaths,
    read_dataframe_with_extension,
    write_dataframe_and_metadata,
    write_functions,
    write_only_dataframe,
)
from xiplot.utils.io import FinallyCloseBytesIO
from xiplot.utils.layouts import layout_wrapper


class Data(Tab):
    @staticmethod
    def register_callbacks(app, df_from_store, df_to_store, data_dir=""):
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
                    default_style={
                        "minHeight": 1,
                        "lineHeight": 4,
                        "height": "85px",
                    },
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
                                        (
                                            " could not be loaded as a data"
                                            f" frame: {err}."
                                        ),
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
                    encode_aux(aux),
                    meta,
                    generate_dataframe_options(upload_path, data_dir),
                    str(Path("uploads") / upload_path.name),
                    [uploader],
                    None,
                )

        except (ImportError, AttributeError):

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
                                        (
                                            " could not be loaded as a data"
                                            f" frame: {err}."
                                        ),
                                    ]
                                )
                            ],
                            action="show",
                            autoClose=10000,
                        ),
                    )

                return (
                    df_to_store(df),
                    encode_aux(aux),
                    meta,
                    generate_dataframe_options(upload_name, data_dir),
                    str(Path("uploads") / upload_name.name),
                    None,
                    None,
                    None,
                )

        @app.callback(
            ServersideOutput("data_frame_store", "data"),
            Output("auxiliary_store", "data"),
            Output("metadata_store", "data"),
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
                if str(list(filepath.parents)[0]) == "uploads":
                    df_store = uploaded_data
                    aux_store = uploaded_aux
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
                    filepath = Path(data_dir) / filepath.name

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
                            dmc.Notification(
                                id=str(uuid.uuid4()),
                                color="yellow",
                                title="Warning",
                                message=(
                                    f"The file {filepath.name} could not be"
                                    f" loaded as a data frame: {err}."
                                ),
                                action="show",
                                autoClose=10000,
                            ),
                        )

                    df_store = df_to_store(df)
                    aux_store = encode_aux(aux)

                    notification = dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="green",
                        title="Success",
                        message=(
                            f"The data file {meta['filename']} was loaded"
                            " successfully!"
                        ),
                        action="show",
                        autoClose=5000,
                    )
            elif trigger == "uploaded_data_file_store":
                df_store = uploaded_data
                aux_store = uploaded_aux
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
                meta["plots"] = OrderedDict()
            meta["session"] = str(uuid.uuid4())

            import jsonschema

            try:
                jsonschema.validate(
                    instance=meta,
                    schema=dict(
                        type="object",
                        properties=dict(
                            filename=dict(type="string"),
                            settings=dict(type="object"),
                            plots=dict(type="object"),
                        ),
                        required=["filename", "settings", "plots"],
                    ),
                )
            except jsonschema.exceptions.ValidationError as err:
                return (
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=(
                            f"The file {filepath.name} has invalid metadata at"
                            f" meta{err.json_path[1:]}: {err.message}."
                        ),
                        action="show",
                        autoClose=10000,
                    ),
                )

            df = df_from_store(df_store)
            aux = decode_aux(aux_store)

            if SELECTED_COLUMN_NAME in aux:
                if aux.dtypes[SELECTED_COLUMN_NAME] != bool:
                    notification = dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=(
                            f"The file {filepath.name} has been loaded but the"
                            ' auxiliary column "{SELECTED_COLUMN_NAME}" is'
                            " not of type bool."
                        ),
                        action="show",
                        autoClose=10000,
                    )

            if CLUSTER_COLUMN_NAME in aux:
                invalid_clusters = set(get_clusters(aux).categories) - set(
                    cluster_colours().keys()
                )
                if len(invalid_clusters) > 0:
                    message = (
                        f"The file {filepath.name} has been loaded"
                        f' but the auxiliary column "{CLUSTER_COLUMN_NAME}"'
                        f" contains invalid values {invalid_clusters}."
                    )
                    notification = dmc.Notification(
                        id=str(uuid.uuid4()),
                        color="yellow",
                        title="Warning",
                        message=message,
                        action="show",
                        autoClose=10000,
                    )

            return (
                df_store,
                aux_store,
                meta,
                notification,
            )

        @app.callback(
            Output("data-download", "data"),
            Output("data-tab-download-notify-container", "children"),
            Input("download-data-file-button", "n_clicks"),
            Input("download-plots-file-button", "n_clicks"),
            State("data_files", "value"),
            State("data_frame_store", "data"),
            State("auxiliary_store", "data"),
            State("metadata_store", "data"),
            State(PlotData.get_id(ALL, ALL), "data"),
            State(generate_id(WriteFormatDropdown), "value"),
            prevent_initial_call=True,
        )
        def download_file(
            d_clicks,
            p_clicks,
            filepath,
            df,
            aux,
            meta,
            plot_data,
            file_extension,
        ):
            df = df_from_store(df)
            aux = decode_aux(aux)

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

            with FinallyCloseBytesIO() as file:
                if ctx.triggered_id == "download-data-file-button":
                    try:
                        filename, mime = write_only_dataframe(
                            df, meta["filename"], file, file_extension
                        )
                    except Exception as err:
                        return dash.no_update, dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="yellow",
                            title="Warning",
                            message=[
                                html.Div(
                                    [
                                        (
                                            "Failed to download the data file"
                                            f" for {filepath.name}"
                                        ),
                                        (
                                            html.I(" (upload)")
                                            if ctx.triggered_id
                                            == "uploaded_data_file_store"
                                            else None
                                        ),
                                        f": {err}.",
                                    ]
                                )
                            ],
                            action="show",
                            autoClose=10000,
                        )

                if ctx.triggered_id == "download-plots-file-button":
                    try:
                        for data in plot_data:
                            index = data["index"]
                            del data["index"]
                            meta["plots"][index] = data

                        filename, mime = write_dataframe_and_metadata(
                            df,
                            aux,
                            meta,
                            meta["filename"],
                            file,
                            file_extension,
                        )
                    except Exception as err:
                        return dash.no_update, dmc.Notification(
                            id=str(uuid.uuid4()),
                            color="yellow",
                            title="Warning",
                            message=[
                                html.Div(
                                    [
                                        (
                                            "Failed to download plots and data"
                                            f" file for {filepath.name}"
                                        ),
                                        (
                                            html.I(" (upload)")
                                            if ctx.triggered_id
                                            == "uploaded_data_file_store"
                                            else None
                                        ),
                                        f": {err}.",
                                    ]
                                )
                            ],
                            action="show",
                            autoClose=10000,
                        )

                encoded = base64.b64encode(file.getvalue()).decode("ascii")

                return (
                    dict(
                        base64=True,
                        content=encoded,
                        filename=filename,
                        type=mime,
                    ),
                    None,
                )

    @staticmethod
    def create_layout(data_dir=""):
        try:
            import dash_uploader as du

            uploader = du.Upload(
                id="file_uploader",
                text="Drag and Drop or Select a File to upload",
                default_style={"minHeight": 1, "lineHeight": 4},
            )
        except (ImportError, AttributeError, NotImplementedError):
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

        return FlexRow(
            html.Div(
                [
                    layout_wrapper(
                        component=FlexRow(
                            dcc.Dropdown(
                                [
                                    {"label": fp.name, "value": str(fp)}
                                    for fp in get_data_filepaths(
                                        data_dir=data_dir
                                    )
                                ],
                                id="data_files",
                            ),
                            html.Button(
                                "Load",
                                id="submit-button",
                                n_clicks=0,
                                className="button",
                            ),
                        ),
                        title="Choose a data file",
                        css_class="dash-dropdown",
                    ),
                    html.Br(),
                    html.Div(
                        [
                            html.Div("Download the data"),
                            FlexRow(
                                html.Button(
                                    "Download only the data",
                                    id="download-data-file-button",
                                    n_clicks=0,
                                    className="button",
                                ),
                                " ",
                                html.Button(
                                    "Download plots and data",
                                    id="download-plots-file-button",
                                    n_clicks=0,
                                    className="button",
                                ),
                                WriteFormatDropdown(),
                            ),
                            dcc.Download(
                                id="data-download",
                            ),
                        ],
                    ),
                ],
                className="stretch",
            ),
            html.Div(
                [uploader],
                id="file_uploader_container",
                className="dash-uploader",
            ),
            id="control_data_content-container",
        )

    @staticmethod
    def create_layout_globals():
        return html.Div(
            [
                dcc.Store(id="uploaded_data_file_store"),
                dcc.Store(id="uploaded_auxiliary_store"),
                dcc.Store(id="uploaded_metadata_store"),
                html.Div(
                    id="data-tab-notify-container", style={"display": "none"}
                ),
                html.Div(
                    id="data-tab-upload-notify-container",
                    style={"display": "none"},
                ),
                html.Div(
                    id="data-tab-download-notify-container",
                    style={"display": "none"},
                ),
            ]
        )


class WriteFormatDropdown(dcc.Dropdown):
    def __init__(self, **kwargs):
        options = [ext for _, ext, _ in write_functions()]
        super().__init__(
            options=options,
            multi=False,
            id=generate_id(type(self)),
            placeholder="File format...",
            **kwargs,
        )


def generate_dataframe_options(upload_path, data_dir):
    return [
        {
            "label": html.Div([upload_path.name, " ", html.I("(upload)")]),
            "value": str(Path("uploads") / upload_path.name),
        }
    ] + [
        {"label": fp.name, "value": str(fp)}
        for fp in get_data_filepaths(data_dir=data_dir)
    ]
