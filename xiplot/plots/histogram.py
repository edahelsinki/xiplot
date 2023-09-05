import pandas as pd
import plotly.express as px
from dash import ALL, MATCH, Input, Output, ctx, dcc
from dash.exceptions import PreventUpdate

from xiplot.plots import APlot
from xiplot.plugin import ID_HOVERED
from xiplot.utils.auxiliary import (
    SELECTED_COLUMN_NAME,
    decode_aux,
    get_clusters,
    merge_df_aux,
)
from xiplot.utils.cluster import cluster_colours
from xiplot.utils.components import (
    ClusterDropdown,
    ColumnDropdown,
    PdfButton,
    PlotData,
)
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.layouts import layout_wrapper


class Histogram(APlot):
    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        PdfButton.register_callback(app, cls.name(), {"type": "histogram"})

        @app.callback(
            Output({"type": "histogram", "index": MATCH}, "figure"),
            Input(cls.get_id(MATCH, "x_axis_dropdown"), "value"),
            Input(ClusterDropdown.get_id(MATCH), "value"),
            Input(ID_HOVERED, "data"),
            Input("data_frame_store", "data"),
            Input("auxiliary_store", "data"),
            Input("plotly-template", "data"),
            prevent_initial_call=False,
        )
        def tmp(x_axis, selected_clusters, hover, df, aux, template=None):
            # Try branch for testing
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except Exception:
                pass

            return Histogram.render(
                x_axis,
                selected_clusters,
                hover,
                df_from_store(df),
                decode_aux(aux),
                template,
            )

        PlotData.register_callback(
            cls.name(),
            app,
            (
                Input(cls.get_id(ALL, "x_axis_dropdown"), "value"),
                Input(ClusterDropdown.get_id(ALL), "value"),
            ),
            lambda i: dict(axes=dict(x=i[0]), classes=i[1] or []),
        )

        ColumnDropdown.register_callback(
            app,
            cls.get_id(ALL, "x_axis_dropdown"),
            df_from_store,
            numeric=True,
        )

        return [tmp]

    @staticmethod
    def render(x_axis, selected_clusters, hover, df, aux, template=None):
        df = merge_df_aux(df, aux)
        clusters = get_clusters(aux, df.shape[0])
        if type(selected_clusters) == str:
            selected_clusters = [selected_clusters]
        if not selected_clusters:
            selected_clusters = clusters.categories

        props_dict = {"all": []}
        for s in selected_clusters:
            if s != "all":
                props_dict[s] = []

        for c, p in zip(clusters, df[x_axis]):
            if c != "all" and c in selected_clusters:
                props_dict[c].append(p)
            props_dict["all"].append(p)

        clusters_col = []
        x = []
        for s in selected_clusters:
            clusters_col += [s for _ in props_dict[s]]
            x += props_dict[s]

        dff = pd.DataFrame({"Clusters": clusters_col, x_axis: x})

        fig_property = px.histogram(
            dff,
            x=x_axis,
            color="Clusters",
            hover_data={
                "Clusters": False,
                x_axis: False,
            },
            color_discrete_map=cluster_colours(),
            opacity=0.5,
            histnorm="probability density",
            template=template,
        )

        fig_property.update_layout(
            hovermode="x unified",
            showlegend=False,
            barmode="overlay",
            yaxis=dict(
                tickformat=".2%",
            ),
        )

        if hover is not None:
            fig_property.add_vline(
                df[x_axis][hover],
                line=dict(color="rgba(0.5,0.5,0.5,0.5)", dash="dash"),
                layer="below",
            )
        if SELECTED_COLUMN_NAME in aux:
            color = "#DDD" if template and "dark" in template else "#333"
            for x in df[x_axis][aux[SELECTED_COLUMN_NAME]]:
                fig_property.add_vline(
                    x, line=dict(color=color, width=0.5), layer="below"
                )

        return fig_property

    @classmethod
    def create_layout(cls, index, df, columns, config=dict()):
        import jsonschema

        jsonschema.validate(
            instance=config,
            schema=dict(
                type="object",
                properties=dict(
                    axes=dict(
                        type="object", properties=dict(x=dict(type="string"))
                    ),
                    classes=dict(
                        type="array",
                        items=dict(enum=list(cluster_colours().keys())),
                        uniqueItems=True,
                    ),
                ),
            ),
        )
        num_columns = get_numeric_columns(df, columns)

        try:
            x_axis = config["axes"]["x"]
        except Exception:
            x_axis = None

        if x_axis is None and len(num_columns) > 0:
            x_axis = num_columns[0]

        if x_axis is None:
            raise Exception("The dataframe contains no numeric columns")

        classes = config.get("classes", [])

        return [
            dcc.Graph(id={"type": "histogram", "index": index}),
            layout_wrapper(
                component=ColumnDropdown(
                    cls.get_id(index, "x_axis_dropdown"),
                    value=x_axis,
                    clearable=False,
                    options=[x_axis],
                ),
                css_class="dd-single",
                title="x axis",
            ),
            layout_wrapper(
                component=ClusterDropdown(
                    index=index, multi=True, value=classes, clearable=True
                ),
                title="Cluster Comparison",
                css_class="dd-single",
            ),
        ]
