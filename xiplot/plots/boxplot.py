import dash
import plotly.express as px
from dash import ALL, MATCH, Input, Output, State, dcc
from dash.exceptions import PreventUpdate

from xiplot.plots import APlot
from xiplot.plugin import (
    ID_AUXILIARY,
    ID_CLICKED,
    ID_HOVERED,
    placeholder_figure,
)
from xiplot.utils.auxiliary import (
    CLUSTER_COLUMN_NAME,
    SELECTED_COLUMN_NAME,
    decode_aux,
    merge_df_aux,
    toggle_selected,
)
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.components import (
    ColumnDropdown,
    FlexRow,
    PdfButton,
    PlotData,
)
from xiplot.utils.dataframe import get_default_column
from xiplot.utils.layouts import layout_wrapper


class Boxplot(APlot):
    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        PdfButton.register_callback(app, cls.name(), cls.get_id(MATCH))

        @app.callback(
            Output(cls.get_id(MATCH), "figure"),
            Input(cls.get_id(MATCH, "x_axis"), "value"),
            Input(cls.get_id(MATCH, "y_axis"), "value"),
            Input(cls.get_id(MATCH, "plot"), "value"),
            Input(cls.get_id(MATCH, "color"), "value"),
            Input(ID_HOVERED, "data"),
            Input("data_frame_store", "data"),
            Input("auxiliary_store", "data"),
            Input("plotly-template", "data"),
            prevent_initial_call=False,
        )
        def render(
            x_axis,
            y_axis,
            plot,
            color,
            hover,
            df,
            aux,
            template=None,
        ):
            return cls.render(
                df_from_store(df),
                decode_aux(aux),
                x_axis,
                y_axis,
                plot,
                color,
                hover,
                template,
            )

        def get_row(hover):
            try:
                for p in hover:
                    if p is not None:
                        return p["points"][0]["customdata"][0]
            except KeyError:
                raise PreventUpdate()
            raise PreventUpdate()

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
            return toggle_selected(aux, row), row

        PlotData.register_callback(
            cls.name(),
            app,
            {
                "x_axis": Input(cls.get_id(MATCH, "x_axis"), "value"),
                "y_axis": Input(cls.get_id(MATCH, "y_axis"), "value"),
                "color": Input(cls.get_id(MATCH, "color"), "value"),
                "plot": Input(cls.get_id(MATCH, "plot"), "value"),
            },
        )

        ColumnDropdown.register_callback(
            app, cls.get_id(ALL, "x_axis"), df_from_store, category=True
        )
        ColumnDropdown.register_callback(
            app, cls.get_id(ALL, "y_axis"), df_from_store, numeric=True
        )
        ColumnDropdown.register_callback(
            app, cls.get_id(ALL, "color"), df_from_store, category=True
        )

        return render

    @staticmethod
    def render(
        df,
        aux,
        x_axis,
        y_axis,
        plot="Box plot",
        color=None,
        hover=None,
        template=None,
    ):
        if x_axis is None or y_axis is None:
            return placeholder_figure("Please select x and y axis")
        df = merge_df_aux(df, aux).reset_index(names="__Xiplot_index__")
        if color not in df.columns:
            color = None
        if plot == "Box plot":
            fig = px.box(
                df,
                x=x_axis,
                y=y_axis,
                color=color,
                notched=True,
                custom_data=["__Xiplot_index__"],
                color_discrete_map=cluster_colours(),
                template=template,
            )
            fig.update_traces(dict(boxmean=True))
        elif plot == "Violin plot":
            fig = px.violin(
                df,
                x=x_axis,
                y=y_axis,
                color=color,
                custom_data=["__Xiplot_index__"],
                color_discrete_map=cluster_colours(),
                template=template,
            )
        elif plot == "Strip chart":
            fig = px.strip(
                df,
                x=x_axis,
                y=y_axis,
                color=color,
                color_discrete_map=cluster_colours(),
                custom_data=["__Xiplot_index__"],
                template=template,
            )
        else:
            return placeholder_figure("Unsupported plot type")

        if hover is not None:
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
    def create_layout(cls, index, df, columns=None, config=dict()):
        num_columns = ColumnDropdown.get_columns(df, numeric=True)
        cat_columns = ColumnDropdown.get_columns(df, category=True)

        x_axis = config.get("x_axis", get_default_column(cat_columns, "x"))
        y_axis = config.get("y_axis", get_default_column(num_columns, "y"))
        color = config.get("color", CLUSTER_COLUMN_NAME)
        plot = config.get("plot", "Box plot")

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
                layout_wrapper(
                    component=dcc.Dropdown(
                        id=cls.get_id(index, "plot"),
                        options=["Box plot", "Violin plot", "Strip chart"],
                        value=plot,
                        clearable=False,
                    ),
                    css_class="dash-dropdown",
                    title="Plot type",
                ),
            ),
        ]
