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
from xiplot.utils.layouts import layout_wrapper


class Distplot(APlot):
    @classmethod
    def name(cls):
        return "Density plot"

    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        PdfButton.register_callback(app, cls.name(), cls.get_id(MATCH))

        @app.callback(
            Output(cls.get_id(MATCH), "figure"),
            Input(cls.get_id(MATCH, "variable"), "value"),
            Input(cls.get_id(MATCH, "color"), "value"),
            Input(ID_HOVERED, "data"),
            Input("data_frame_store", "data"),
            Input("auxiliary_store", "data"),
            Input("plotly-template", "data"),
            prevent_initial_call=False,
        )
        def render(
            variable,
            color,
            hover,
            df,
            aux,
            template=None,
        ):
            return cls.render(
                df_from_store(df),
                decode_aux(aux),
                variable,
                color,
                hover,
                template,
            )

        def get_row(hover):
            try:
                for p in hover:
                    if p is not None:
                        return p["points"][0]["customdata"]
            except (KeyError, TypeError):
                raise PreventUpdate()
            raise PreventUpdate()

        @app.callback(
            Output(ID_HOVERED, "data"),
            Output(cls.get_id(ALL), "hoverData"),
            Input(cls.get_id(ALL), "hoverData"),
        )
        def handle_hover_events(hover):
            return get_row(hover), [None] * len(hover)

        @app.callback(
            Output(ID_AUXILIARY, "data"),
            Output(ID_CLICKED, "data"),
            Output(cls.get_id(ALL), "clickData"),
            Input(cls.get_id(ALL), "clickData"),
            State(ID_AUXILIARY, "data"),
        )
        def handle_click_events(click, aux):
            row = get_row(click)
            if aux is None:
                return dash.no_update, row
            return toggle_selected(aux, row), row, [None] * len(click)

        PlotData.register_callback(
            cls.name(),
            app,
            {
                "variable": Input(cls.get_id(MATCH, "variable"), "value"),
                "color": Input(cls.get_id(MATCH, "color"), "value"),
            },
        )

        ColumnDropdown.register_callback(
            app, cls.get_id(ALL, "variable"), df_from_store, numeric=True
        )
        ColumnDropdown.register_callback(
            app, cls.get_id(ALL, "color"), df_from_store, category=True
        )

        return render, handle_hover_events, handle_click_events

    @staticmethod
    def render(
        df,
        aux,
        variable,
        color=None,
        hover=None,
        template=None,
    ):
        # `plotly.figure_factory` checks if scipy is installed and caches the
        # result. This causes issues if scipy is lazily loaded in WASM.
        import scipy  # noqa: F401, isort: skip
        import plotly.figure_factory as ff

        df = merge_df_aux(df, aux)
        df["__Xiplot_index__"] = range(df.shape[0])
        if variable not in df.columns:
            return placeholder_figure("Please select a variable")
        if color not in df.columns:
            fig = ff.create_distplot(
                [df[variable]], [variable], show_hist=False
            )
            fig.update_layout(
                template=template,
                showlegend=False,
                xaxis_title=variable,
                yaxis_title="Density",
                yaxis_domain=[0.11, 1],
                yaxis2_domain=[0, 0.09],
            )
            fig.data[1]["customdata"] = df["__Xiplot_index__"]

        else:
            df[color] = df[color].astype("category")
            df2 = df.groupby(color)
            cats = [
                c
                for c in df[color].cat.categories
                if df2[variable].get_group(c).std() > 1e-6
            ]
            data = [df2[variable].get_group(g) for g in cats]
            customdata = [df2["__Xiplot_index__"].get_group(g) for g in cats]
            groups = [str(g) for g in cats]
            colors1 = px.colors.qualitative.Plotly
            colors2 = cluster_colours()
            colors = []
            for i, n in enumerate(groups):
                colors.append(colors2.get(n, colors1[i % len(colors1)]))
            fig = ff.create_distplot(
                data, groups, show_hist=False, colors=colors
            )
            fig.update_layout(
                template=template,
                legend=dict(title=color, traceorder="normal"),
                xaxis_title=variable,
                yaxis_title="Density",
                yaxis_domain=[0.16, 1] if len(cats) < 4 else [0.26, 1],
                yaxis2_domain=[0, 0.14] if len(cats) < 4 else [0, 0.24],
            )
            for i, d in enumerate(customdata):
                fig.data[i + len(cats)]["customdata"] = d

        if hover is not None:
            fig.add_vline(
                df[variable][hover],
                line=dict(color="rgba(0.5,0.5,0.5,0.5)", dash="dash"),
                layer="below",
            )
        if SELECTED_COLUMN_NAME in aux:
            sel_color = "#DDD" if template and "dark" in template else "#333"
            for x in df[variable][aux[SELECTED_COLUMN_NAME]]:
                fig.add_vline(
                    x, line=dict(color=sel_color, width=0.5), layer="below"
                )
            x = df[variable][aux[SELECTED_COLUMN_NAME]]
            fig.add_scatter(
                x=x,
                y=(
                    [variable] * len(x)
                    if color not in df.columns
                    else df[color][aux[SELECTED_COLUMN_NAME]]
                ),
                marker=dict(color=sel_color, size=8),
                yaxis="y2",
                hoverinfo="skip",
                hovertemplate=None,
                mode="markers",
                showlegend=False,
            )
        return fig

    @classmethod
    def create_layout(cls, index, df, columns=None, config=dict()):
        num_columns = ColumnDropdown.get_columns(df, numeric=True)

        variable = config.get(
            "variable", num_columns[0] if num_columns else None
        )
        color = config.get("color", CLUSTER_COLUMN_NAME)

        return [
            dcc.Graph(id=cls.get_id(index)),
            FlexRow(
                layout_wrapper(
                    component=ColumnDropdown(
                        cls.get_id(index, "variable"),
                        options=num_columns,
                        value=variable,
                        clearable=False,
                    ),
                    css_class="dash-dropdown",
                    title="Variable",
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
