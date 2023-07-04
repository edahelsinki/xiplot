import jsonschema
import plotly.express as px
from dash import MATCH, Input, Output, ctx, dcc, html
from dash.exceptions import PreventUpdate

from xiplot.plots import APlot
from xiplot.utils.auxiliary import decode_aux, merge_df_aux
from xiplot.utils.cluster import KMeans
from xiplot.utils.components import (
    ColumnDropdown,
    FlexRow,
    PdfButton,
    PlotData,
)
from xiplot.utils.dataframe import get_numeric_columns
from xiplot.utils.layouts import layout_wrapper
from xiplot.utils.regex import get_columns_by_regex


class Heatmap(APlot):
    @classmethod
    def register_callbacks(cls, app, df_from_store, df_to_store):
        PdfButton.register_callback(app, cls.name(), {"type": "heatmap"})

        @app.callback(
            Output({"type": "heatmap", "index": MATCH}, "figure"),
            Input({"type": "heatmap_cluster_amount", "index": MATCH}, "value"),
            Input(cls.get_id(MATCH, "columns_dropdown"), "value"),
            Input("data_frame_store", "data"),
            Input("auxiliary_store", "data"),
            Input("plotly-template", "data"),
            prevent_initial_call=False,
        )
        def tmp(n_clusters, features, df, aux, template=None):
            # Try branch for testing
            try:
                if ctx.triggered_id == "data_frame_store":
                    raise PreventUpdate()
            except PreventUpdate:
                raise
            except Exception:
                pass

            return Heatmap.render(
                n_clusters,
                features,
                df_from_store(df),
                decode_aux(aux),
                template,
            )

        ColumnDropdown.register_callback(
            app,
            cls.get_id(MATCH, "columns_dropdown"),
            df_from_store,
            numeric=True,
            regex_button_id=cls.get_id(MATCH, "regex_button"),
            regex_input_id=cls.get_id(MATCH, "regex_input"),
        )

        PlotData.register_callback(
            cls.name(),
            app,
            dict(
                clusters=Input(
                    {"type": "heatmap_cluster_amount", "index": MATCH}, "value"
                ),
                columns=Input(cls.get_id(MATCH, "columns_dropdown"), "value"),
            ),
        )

        return [tmp]

    @staticmethod
    def render(n_clusters, features, df, aux, template=None):
        km = KMeans(n_clusters=n_clusters, random_state=42)
        df = merge_df_aux(df, aux)
        dff = df.dropna()

        features = get_columns_by_regex(dff.columns.to_list(), features)

        features = features if features else df.columns.to_list()
        features = get_numeric_columns(dff, features)

        km.fit(dff[features])

        cluster_centers = km.cluster_centers_

        fig = px.imshow(
            cluster_centers,
            x=features,
            y=[str(n + 1) for n in range(n_clusters)],
            color_continuous_scale="RdBu",
            origin="lower",
            aspect="auto",
            template=template,
        )
        return fig

    @classmethod
    def create_layout(cls, index, df, columns, config=dict()):
        jsonschema.validate(
            instance=config,
            schema=dict(
                type="object", properties=dict(clusters=dict(type="integer"))
            ),
        )
        n_clusters = config.get("clusters", 5)
        num_columns = get_numeric_columns(df, columns)
        return [
            dcc.Graph(id={"type": "heatmap", "index": index}),
            FlexRow(
                layout_wrapper(
                    component=ColumnDropdown(
                        cls.get_id(index, "columns_dropdown"),
                        options=num_columns,
                        multi=True,
                        clearable=False,
                        value=config.get("columns", None),
                    ),
                    title="Features",
                    css_class="dash-dropdown",
                ),
                html.Button(
                    "Add features by regex",
                    id=cls.get_id(index, "regex_button"),
                    className="button",
                ),
                layout_wrapper(
                    component=dcc.Slider(
                        min=2,
                        max=10,
                        step=1,
                        value=n_clusters,
                        id={"type": "heatmap_cluster_amount", "index": index},
                    ),
                    title="Number of clusters",
                    css_class="dash-dropdown",
                ),
            ),
            dcc.Input(
                id=cls.get_id(index, "regex_input"), style={"display": "none"}
            ),
        ]
