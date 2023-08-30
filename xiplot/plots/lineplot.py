import dash
import plotly.express as px
from dash import ALL, MATCH, Input, Output, State, ctx, dcc
from dash.exceptions import PreventUpdate

from xiplot.plots import APlot
from xiplot.plugin import ID_AUXILIARY, ID_CLICKED, ID_HOVERED
from xiplot.utils.auxiliary import (
    CLUSTER_COLUMN_NAME,
    SELECTED_COLUMN_NAME,
    decode_aux,
    encode_aux,
    get_selected,
    merge_df_aux,
)
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.components import (
    ColumnDropdown,
    FlexRow,
    PdfButton,
    PlotData,
)
from xiplot.utils.dataframe import get_default_xy_columns, get_numeric_columns
from xiplot.utils.layouts import layout_wrapper


class Lineplot(APlot):
    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        PdfButton.register_callback(app, cls.name(), cls.get_id(MATCH))

        @app.callback(
            Output(cls.get_id(MATCH), "figure"),
            Input(cls.get_id(MATCH, "x_axis"), "value"),
            Input(cls.get_id(MATCH, "y_axis"), "value"),
            Input(cls.get_id(MATCH, "color"), "value"),
            Input(ID_HOVERED, "data"),
            Input("data_frame_store", "data"),
            Input("auxiliary_store", "data"),
            Input("plotly-template", "data"),
            prevent_initial_call=False,
        )
        def tmp(
            x_axis,
            y_axis,
            color,
            hover,
            df,
            aux,
            template=None,
        ):
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except Exception:
                pass

            fig = cls.render(
                df_from_store(df),
                decode_aux(aux),
                x_axis,
                y_axis,
                color,
                hover,
                template,
            )

            if fig is None:
                return dash.no_update

            return fig

        def get_row(hover):
            row = None
            for p in (p for p in hover if p is not None):
                row = p["points"][0]["customdata"][0]
            if row is None:
                raise PreventUpdate()
            return row

        @app.callback(
            Output(ID_HOVERED, "data"), Input(cls.get_id(ALL), "hoverData")
        )
        def handle_hover_events(hover):
            return get_row(hover)

        @app.callback(
            Output(ID_AUXILIARY, "data"),
            Output(ID_CLICKED, "data"),
            Input(cls.get_id(ALL), "clickData"),
            State(ID_AUXILIARY, "data"),
        )
        def handle_click_events(click, aux):
            row = get_row(click)
            if aux is None:
                return dash.no_update, row

            aux = decode_aux(aux)
            selected = get_selected(aux)
            selected[row] = not selected[row]
            aux[SELECTED_COLUMN_NAME] = selected

            return encode_aux(aux), row

        PlotData.register_callback(
            cls.name(),
            app,
            {
                "x_axis": Input(cls.get_id(MATCH, "x_axis"), "value"),
                "y_axis": Input(cls.get_id(MATCH, "y_axis"), "value"),
                "color": Input(cls.get_id(MATCH, "color"), "value"),
            },
        )

        ColumnDropdown.register_callback(
            app, cls.get_id(ALL, "x_axis"), df_from_store, numeric=True
        )
        ColumnDropdown.register_callback(
            app, cls.get_id(ALL, "y_axis"), df_from_store, numeric=True
        )
        ColumnDropdown.register_callback(
            app, cls.get_id(ALL, "color"), df_from_store, category=True
        )

        return tmp, handle_hover_events, handle_click_events

    @staticmethod
    def render(
        df,
        aux,
        x_axis,
        y_axis,
        color=None,
        hover=None,
        template=None,
    ):
        df = merge_df_aux(df, aux).reset_index(names="__Xiplot_index__")
        if color not in df.columns:
            color = None
        fig = px.line(
            df.sort_values(by=x_axis),
            x=x_axis,
            y=y_axis,
            color=color,
            color_discrete_map=cluster_colours(),
            custom_data=["__Xiplot_index__"],
            template=template,
        )
        if hover is not None:
            fig.add_vline(
                df[x_axis][hover],
                line=dict(color="rgba(0.5,0.5,0.5,0.5)", dash="dash"),
            )
            fig.add_hline(
                df[y_axis][hover],
                line=dict(color="rgba(0.5,0.5,0.5,0.5)", dash="dash"),
            )
        if SELECTED_COLUMN_NAME in aux:
            trace = px.scatter(
                df[aux[SELECTED_COLUMN_NAME]], x=x_axis, y=y_axis, symbol=color
            )
            trace.update_traces(
                hoverinfo="skip",
                hovertemplate=None,
                marker=dict(
                    size=15,
                    color=(
                        "#DDD" if template and "dark" in template else "#333"
                    ),
                ),
            )
            fig.add_traces(trace.data)
        return fig

    @classmethod
    def create_layout(cls, index, df, columns, config=dict()):
        num_columns = get_numeric_columns(df, columns)

        x_axis, y_axis = get_default_xy_columns(num_columns)
        x_axis = config.get("x_axis", x_axis)
        y_axis = config.get("y_axis", y_axis)
        color = config.get("color", CLUSTER_COLUMN_NAME)

        if x_axis is None or y_axis is None:
            raise Exception("The dataframe contains no numeric columns")

        return [
            dcc.Graph(id=cls.get_id(index)),
            FlexRow(
                layout_wrapper(
                    component=ColumnDropdown(
                        cls.get_id(index, "x_axis"),
                        options=num_columns,
                        value=x_axis,
                        clearable=False,
                    ),
                    css_class="dash-dropdown",
                    title="X",
                ),
                layout_wrapper(
                    component=ColumnDropdown(
                        cls.get_id(index, "y_axis"),
                        options=num_columns,
                        value=y_axis,
                        clearable=False,
                    ),
                    css_class="dash-dropdown",
                    title="Y",
                ),
                layout_wrapper(
                    component=ColumnDropdown(
                        cls.get_id(index, "color"),
                        options=columns,
                        value=color,
                        clearable=True,
                    ),
                    css_class="dash-dropdown",
                    title="Groups",
                ),
            ),
        ]
