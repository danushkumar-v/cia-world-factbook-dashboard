"""
Application Callbacks
All Dash callbacks for interactivity
"""
from dash import Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html
import plotly.express as px
import logging
from typing import Optional


logger = logging.getLogger(__name__)


def register_callbacks(app, merged_data, metrics_info, viz_factory):
    """Register all application callbacks"""

    def _get_default_metric():
        """Get default metric if none selected"""
        first_category = next(iter(metrics_info), None)
        if first_category and metrics_info[first_category]:
            return metrics_info[first_category][0].get('name')
        return None

    def _normalize_multi(value):
        if value is None:
            return []
        if isinstance(value, (list, tuple, set)):
            return [v for v in value if v]
        return [value]

    def _safe_figure(message: str, theme: Optional[str] = None, height: int = 260) -> go.Figure:
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            align="center",
            font=dict(size=13),
        )
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=height)
        return viz_factory.apply_theme(fig, theme)

    def _apply_filters(df: pd.DataFrame, continents, dev_levels) -> pd.DataFrame:
        out = df
        conts = _normalize_multi(continents)
        devs = _normalize_multi(dev_levels)
        if conts and "Continent" in out.columns:
            out = out[out["Continent"].astype(str).isin([str(c) for c in conts])]
        if devs and "Development_Level" in out.columns:
            out = out[out["Development_Level"].astype(str).isin([str(d) for d in devs])]
        return out

    # ------------------------------------------------------------
    # UI theme switching (light/dark)
    # ------------------------------------------------------------
    @app.callback(
        Output("ui-theme", "data"),
        Output("app-root", "className"),
        Input("theme-toggle", "value"),
        prevent_initial_call=False,
    )
    def set_theme(is_dark):
        theme = "dark" if is_dark else "light"
        return theme, f"theme-{theme}"
    
    @app.callback(
        Output('metric-selector', 'options'),
        Output('metric-selector', 'value'),
        Input('domain-selector', 'value'),
        prevent_initial_call=False,
    )
    def update_metric_options(domain):
        """Update metric options based on selected domain"""
        if domain and domain in metrics_info:
            metrics = metrics_info[domain]
            options = [{'label': m['label'], 'value': m['name']} for m in metrics]
            default_value = metrics[0]['name'] if metrics else None
            return options, default_value
        # Return first domain's metrics if domain is None
        first_domain = next(iter(metrics_info)) if metrics_info else None
        if first_domain:
            metrics = metrics_info[first_domain]
            options = [{'label': m['label'], 'value': m['name']} for m in metrics]
            default_value = metrics[0]['name'] if metrics else None
            return options, default_value
        return [], None

    @app.callback(
        Output('comparison-metric-selector', 'options'),
        Input('domain-selector', 'value'),
        prevent_initial_call=False,
    )
    def update_comparison_metrics(domain):
        """Update comparison metrics options"""
        all_metrics = []
        for cat, metrics in metrics_info.items():
            for metric in metrics:
                all_metrics.append({'label': f"{cat}: {metric['label']}", 'value': metric['name']})
        return all_metrics

    @app.callback(
        Output('correlation-x-selector', 'options'),
        Output('correlation-y-selector', 'options'),
        Output('correlation-x-selector', 'value'),
        Output('correlation-y-selector', 'value'),
        Input('domain-selector', 'value'),
        prevent_initial_call=False,
    )
    def update_correlation_options(domain):
        """Update correlation metric options"""
        all_metrics = []
        for cat, metrics in metrics_info.items():
            for metric in metrics:
                all_metrics.append({'label': f"{cat}: {metric['label']}", 'value': metric['name']})
        
        default_x = 'Real_GDP_per_Capita_USD' if any(m['value'] == 'Real_GDP_per_Capita_USD' for m in all_metrics) else all_metrics[0]['value']
        default_y = 'internet_users_total' if any(m['value'] == 'internet_users_total' for m in all_metrics) else all_metrics[1]['value'] if len(all_metrics) > 1 else all_metrics[0]['value']
        
        return all_metrics, all_metrics, default_x, default_y

    @app.callback(
        Output('continent-filter', 'options'),
        Output('development-filter', 'options'),
        Input('domain-selector', 'value'),
        prevent_initial_call=False,
    )
    def update_filter_options(domain):
        """Update filter dropdown options"""
        try:
            if "Continent" in merged_data.columns:
                continents = sorted(merged_data["Continent"].dropna().unique())
                continents = [c for c in continents if c != "Other"]
                continent_options = [{"label": cont, "value": cont} for cont in continents]
            else:
                continent_options = []

            if "Development_Level" in merged_data.columns:
                dev_levels = merged_data["Development_Level"].dropna().unique()
                dev_options = [{"label": str(level), "value": str(level)} for level in dev_levels]
            else:
                dev_options = []

            return continent_options, dev_options
        except Exception:
            logger.exception("Failed to build filter options")
            return [], []

    @app.callback(
        Output('main-visualization', 'figure'),
        Input('metric-selector', 'value'),
        Input('viz-type-selector', 'value'),
        Input('color-scheme-selector', 'value'),
        Input('continent-filter', 'value'),
        Input('development-filter', 'value'),
        Input('selected-country', 'data'),
        Input('ui-theme', 'data'),
        prevent_initial_call=False,
    )
    def update_main_visualization(metric, viz_type, color_scheme, continents, dev_levels, selected_country, theme):
        """Update main visualization (heavy). Hover effects are handled by a separate overlay."""

        # Use default metric if none selected
        if not metric:
            # Get first available metric from first category
            first_category = next(iter(metrics_info), None)
            if first_category and metrics_info[first_category]:
                metric = metrics_info[first_category][0].get('name')
            if not metric:
                return _safe_figure("Please select a metric to visualize.", theme, height=560)

        # Use default values for viz_type and color_scheme if not provided
        if not viz_type:
            viz_type = 'choropleth'
        if not color_scheme:
            color_scheme = 'Viridis'

        try:
            df_filtered = _apply_filters(merged_data.copy(), continents, dev_levels)
            if metric not in df_filtered.columns:
                return _safe_figure("Selected metric is not available.", theme, height=560)
            if df_filtered.dropna(subset=[metric]).empty:
                return _safe_figure("No data available for the current filters.", theme, height=560)
            title = f"{metric.replace('_', ' ').title()} - Global Distribution"

            # ---- Build the base figure (your normal behavior) ----
            if viz_type == 'choropleth':
                fig = viz_factory.create_choropleth_map(df_filtered, metric, title, color_scheme)
                fig.update_layout(
                    uirevision=f"main-{metric}-{viz_type}-{color_scheme}",
                    datarevision=f"main-{metric}-{viz_type}-{color_scheme}",
                )

                # Highlight clicked/selected country (no hover overlay; avoids artifacts)
                if selected_country:
                    fig.add_trace(
                        go.Choropleth(
                            locations=[selected_country],
                            z=[1],
                            locationmode="country names",
                            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                            showscale=False,
                            hoverinfo="skip",
                            marker_line_color="rgba(255,107,107,0.95)",
                            marker_line_width=5,
                            zmin=0,
                            zmax=1,
                        )
                    )

                return viz_factory.apply_theme(fig, theme)

            elif viz_type == 'globe':
                fig = viz_factory.create_3d_globe(df_filtered, metric, title, color_scheme=color_scheme)
                fig.update_layout(
                    uirevision=f"main-{metric}-{viz_type}-{color_scheme}",
                    datarevision=f"main-{metric}-{viz_type}-{color_scheme}",
                )
                return viz_factory.apply_theme(fig, theme)

            elif viz_type == 'sunburst':
                fig = viz_factory.create_sunburst_chart(df_filtered, metric)
                fig.update_layout(
                    uirevision=f"main-{metric}-{viz_type}-{color_scheme}",
                    datarevision=f"main-{metric}-{viz_type}-{color_scheme}",
                )
                return viz_factory.apply_theme(fig, theme)

            elif viz_type == 'regional':
                fig = viz_factory.create_regional_bar_chart(df_filtered, metric)
                fig.update_layout(
                    uirevision=f"main-{metric}-{viz_type}-{color_scheme}",
                    datarevision=f"main-{metric}-{viz_type}-{color_scheme}",
                )
                return viz_factory.apply_theme(fig, theme)

            # fallback
            fig = viz_factory.create_choropleth_map(df_filtered, metric, title, color_scheme)
            fig.update_layout(
                uirevision=f"main-{metric}-{viz_type}-{color_scheme}",
                datarevision=f"main-{metric}-{viz_type}-{color_scheme}",
            )
            return viz_factory.apply_theme(fig, theme)
        except Exception:
            logger.exception("main-visualization failed for metric=%s viz_type=%s", metric, viz_type)
            return _safe_figure("Unable to render map. Check that the metric has valid data.", theme, height=560)


    @app.callback(
        Output('comparison-chart', 'figure'),
        Input('countries-selector', 'value'),
        Input('comparison-metric-selector', 'value'),
        Input('comparison-chart-type', 'value'),
        Input('ui-theme', 'data'),
        prevent_initial_call=False,
    )
    def update_comparison_chart(countries, metrics, chart_type, theme):
        """Update country comparison chart"""
        try:
            # Normalize inputs
            if countries is None:
                countries = []
            if isinstance(countries, str):
                countries = [countries]

            if metrics is None:
                metrics_list = []
            elif isinstance(metrics, list):
                metrics_list = [m for m in metrics if m]
            else:
                metrics_list = [metrics]

            if not countries or len(countries) < 2:
                return _safe_figure("Please select at least 2 countries to compare", theme, height=400)

            if chart_type == "radar":
                if len(metrics_list) < 3:
                    return _safe_figure(
                        "Radar needs at least 3 metrics. Select 3–8 metrics or switch to Bar Chart.",
                        theme,
                        height=420,
                    )
                # Keep radar readable
                metrics_list = metrics_list[:10]
                return viz_factory.apply_theme(viz_factory.create_comparison_radar(merged_data, countries, metrics_list), theme)

            elif chart_type == "bar":
                if len(metrics_list) < 1:
                    return _safe_figure("Please select at least 1 metric to compare", theme, height=400)
                metric = metrics_list[0]
                return viz_factory.apply_theme(viz_factory.create_comparison_bar(merged_data, countries, metric), theme)

            else:
                return _safe_figure("Unknown chart type selected", theme, height=400)
        except Exception:
            logger.exception("comparison-chart failed countries=%s metric=%s", countries, metrics)
            return _safe_figure("Unable to render comparison chart.", theme, height=400)

    @app.callback(
        Output('correlation-chart', 'figure'),
        Output('heatmap-chart', 'figure'),
        Input('correlation-x-selector', 'value'),
        Input('correlation-y-selector', 'value'),
        Input('correlation-color-selector', 'value'),
        Input('correlation-groupby-selector', 'value'),
        Input('ui-theme', 'data'),
        prevent_initial_call=False,
    )
    def update_correlation_chart(x_metric, y_metric, color_by, facet_by, theme):
        """Update correlation scatter plot"""
        if not x_metric or not y_metric:
            empty = _safe_figure("Select X and Y metrics for correlation analysis.", theme, height=400)
            return empty, empty

        try:
            scatter_fig = viz_factory.apply_theme(
                viz_factory.create_scatter_correlation(
                    merged_data,
                    x_metric,
                    y_metric,
                    color_by=color_by,
                    facet_by=facet_by,
                ),
                theme,
            )
            heatmap_fig = viz_factory.apply_theme(
                viz_factory.create_heatmap_correlation(merged_data, metrics=[x_metric, y_metric]),
                theme,
            )
            return scatter_fig, heatmap_fig
        except Exception:
            logger.exception("correlation-chart failed x=%s y=%s", x_metric, y_metric)
            empty = _safe_figure("Unable to render correlation.", theme, height=400)
            return empty, empty

    @app.callback(
        Output('regional-chart', 'figure'),
        Input('metric-selector', 'value'),
        Input('ui-theme', 'data'),
        prevent_initial_call=False,
    )
    def update_regional_chart(metric, theme):
        """Update regional comparison chart"""
        if not metric:
            metric = _get_default_metric()
            if not metric:
                return _safe_figure("No metric available", theme, height=320)
        try:
            return viz_factory.apply_theme(viz_factory.create_regional_bar_chart(merged_data, metric, "mean"), theme)
        except Exception:
            logger.exception("regional-chart failed for metric=%s", metric)
            return _safe_figure("Unable to render regional chart for this metric.", theme, height=320)


    # ------------------------------------------------------------
    # Overview – ranking, scatter, regional summary
    # ------------------------------------------------------------
    @app.callback(
        Output("rank-chart", "figure"),
        Input("metric-selector", "value"),
        Input("continent-filter", "value"),
        Input("development-filter", "value"),
        Input("selected-country", "data"),
        Input("ui-theme", "data"),
        prevent_initial_call=False,
    )
    def update_rank_chart(metric, continents, dev_levels, selected_country, theme):
        if not metric:
            metric = _get_default_metric()
            if not metric:
                return _safe_figure("No metric available", theme, height=300)

        try:
            df_filtered = _apply_filters(merged_data.copy(), continents, dev_levels)
            fig = viz_factory.create_ranking_bar(
                df=df_filtered,
                metric=metric,
                mode="top",
                n=12,
                selected_country=selected_country,
            )
            return viz_factory.apply_theme(fig, theme)
        except Exception:
            logger.exception("rank-chart failed for metric=%s", metric)
            return _safe_figure("Unable to render ranking for this metric.", theme, height=300)


    @app.callback(
        Output("overview-scatter", "figure"),
        Input("metric-selector", "value"),
        Input("domain-selector", "value"),
        Input("continent-filter", "value"),
        Input("development-filter", "value"),
        Input("selected-country", "data"),
        Input("ui-theme", "data"),
        prevent_initial_call=False,
    )
    def update_overview_scatter(metric, domain, continents, dev_levels, selected_country, theme):
        if not metric:
            metric = _get_default_metric()
            if not metric:
                return _safe_figure("No metric available", theme, height=300)

        try:
            df_filtered = _apply_filters(merged_data.copy(), continents, dev_levels)

            # Smarter reference metric by domain
            domain = domain or ""
            reference_by_domain = {
                "Economy": "Real_GDP_per_Capita_USD",
                "Demographics": "Real_GDP_per_Capita_USD",
                "Communications": "Real_GDP_per_Capita_USD",
                "Energy": "Real_GDP_per_Capita_USD",
                "Infrastructure": "Real_GDP_per_Capita_USD",
                # Geography often makes more sense vs population
                "Geography": "Total_Population",
            }

            ref = reference_by_domain.get(domain, "Real_GDP_per_Capita_USD")
            if ref not in df_filtered.columns:
                ref = "Real_GDP_per_Capita_USD" if "Real_GDP_per_Capita_USD" in df_filtered.columns else metric

            fig = viz_factory.create_metric_vs_reference_scatter(
                df=df_filtered,
                metric=metric,
                reference_metric=ref,
                color_by="Continent" if "Continent" in df_filtered.columns else None,
                selected_country=selected_country,
            )
            return viz_factory.apply_theme(fig, theme)
        except Exception:
            logger.exception("overview-scatter failed for metric=%s domain=%s", metric, domain)
            return _safe_figure("Unable to render relationship view for this metric.", theme, height=300)


    @app.callback(
        Output("overview-regional", "figure"),
        Input("metric-selector", "value"),
        Input("continent-filter", "value"),
        Input("development-filter", "value"),
        Input("ui-theme", "data"),
        prevent_initial_call=False,
    )
    def update_overview_regional(metric, continents, dev_levels, theme):
        if not metric:
            metric = _get_default_metric()
            if not metric:
                return _safe_figure("No metric available", theme, height=320)

        try:
            df_filtered = _apply_filters(merged_data.copy(), continents, dev_levels)
            fig = viz_factory.create_regional_bar_chart(df_filtered, metric, agg="mean")
            fig.update_layout(title=dict(text="Regional Summary (Mean)", x=0.01, xanchor="left"))
            return viz_factory.apply_theme(fig, theme)
        except Exception:
            logger.exception("overview-regional failed for metric=%s", metric)
            return _safe_figure("Unable to render regional summary.", theme, height=320)


    @app.callback(
        Output("overview-spread", "figure"),
        Input("metric-selector", "value"),
        Input("continent-filter", "value"),
        Input("development-filter", "value"),
        Input("selected-country", "data"),
        Input("ui-theme", "data"),
        prevent_initial_call=False,
    )
    def update_overview_spread(metric, continents, dev_levels, selected_country, theme):
        if not metric:
            metric = _get_default_metric()
            if not metric:
                return _safe_figure("No metric available", theme, height=260)

        try:
            df_filtered = _apply_filters(merged_data.copy(), continents, dev_levels)
            dff = df_filtered.dropna(subset=[metric])
            if dff.empty or "Continent" not in dff.columns:
                return _safe_figure("No data available for spread view.", theme, height=260)

            fig = px.box(
                dff,
                x="Continent",
                y=metric,
                points="outliers",
                hover_name="Country" if "Country" in dff.columns else None,
                title="",
            )

            # Highlight selected country value (as a marker)
            if selected_country and "Country" in dff.columns and selected_country in set(dff["Country"]):
                row = dff[dff["Country"] == selected_country].iloc[0]
                cont = row.get("Continent")
                val = row.get(metric)
                if cont is not None and val is not None and val == val:
                    fig.add_trace(
                        go.Scatter(
                            x=[cont],
                            y=[val],
                            mode="markers",
                            name=selected_country,
                            marker=dict(size=12, color="rgba(255,107,107,1)", line=dict(width=2, color="white")),
                            hovertemplate=f"<b>{selected_country}</b><br>%{{x}}<br>%{{y:,.2f}}<extra></extra>",
                        )
                    )

            fig.update_layout(
                title=dict(text="Spread Snapshot (Box plot)", x=0.01, xanchor="left"),
                margin=dict(l=20, r=10, t=50, b=20),
                height=260,
            )
            fig.update_xaxes(tickangle=0)
            return viz_factory.apply_theme(fig, theme)
        except Exception:
            logger.exception("overview-spread failed for metric=%s", metric)
            return _safe_figure("Unable to render spread snapshot.", theme, height=260)


    # ------------------------------------------------------------
    # Overview – insights panel
    # ------------------------------------------------------------
    @app.callback(
        Output("insights-kpis", "children"),
        Output("insights-text", "children"),
        Input("metric-selector", "value"),
        Input("continent-filter", "value"),
        Input("development-filter", "value"),
        Input("selected-country", "data"),
        prevent_initial_call=False,
    )
    def update_insights(metric, continents, dev_levels, selected_country):
        if not metric:
            metric = _get_default_metric()
            if not metric:
                return (
                    dbc.Row([dbc.Col(dbc.Alert("No metric available.", color="warning"), width=12)]),
                    "Select a metric to see insights.",
                )

        df_filtered = _apply_filters(merged_data.copy(), continents, dev_levels)

        series = df_filtered[metric]
        non_null = series.dropna()
        coverage = 0.0 if len(series) == 0 else (len(non_null) / len(series)) * 100.0

        if non_null.empty:
            return (
                dbc.Row(
                    [dbc.Col(dbc.Alert("No valid data for current metric + filters.", color="warning"), width=12)]
                ),
                "Try a different metric or relax filters.",
            )

        top = df_filtered.dropna(subset=[metric]).sort_values(metric, ascending=False).head(3)
        bottom = df_filtered.dropna(subset=[metric]).sort_values(metric, ascending=True).head(3)

        # Summary stats
        try:
            median = float(non_null.median())
        except Exception:
            median = None

        try:
            q1 = float(non_null.quantile(0.25))
            q3 = float(non_null.quantile(0.75))
            iqr = q3 - q1
            outliers = non_null[(non_null < (q1 - 1.5 * iqr)) | (non_null > (q3 + 1.5 * iqr))]
            outlier_count = int(len(outliers))
        except Exception:
            outlier_count = None

        # Compact KPI tiles
        kpis = dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div("Coverage", className="mini-kpi-label"),
                                html.Div(f"{coverage:.0f}%", className="mini-kpi-value"),
                            ]
                        ),
                        className="mini-kpi",
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div("Median", className="mini-kpi-label"),
                                html.Div(
                                    "N/A" if median is None else f"{median:,.2f}",
                                    className="mini-kpi-value",
                                ),
                            ]
                        ),
                        className="mini-kpi",
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div("Countries", className="mini-kpi-label"),
                                html.Div(f"{df_filtered['Country'].nunique()}", className="mini-kpi-value"),
                            ]
                        ),
                        className="mini-kpi",
                    ),
                    width=6,
                    className="mt-2",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div("Outliers", className="mini-kpi-label"),
                                html.Div(
                                    "N/A" if outlier_count is None else f"{outlier_count}",
                                    className="mini-kpi-value",
                                ),
                            ]
                        ),
                        className="mini-kpi",
                    ),
                    width=6,
                    className="mt-2",
                ),
            ],
            className="g-2",
        )

        bullets = []
        if selected_country:
            row = df_filtered[df_filtered["Country"] == selected_country]
            if not row.empty and metric in row.columns:
                val = row.iloc[0].get(metric)
                bullets.append(html.Li([html.B(selected_country), f" selected — {val}"]))

        if not top.empty:
            top_country = top.iloc[0]["Country"]
            top_val = top.iloc[0].get(metric)
            bullets.append(html.Li([html.B("Leader: "), f"{top_country} ({top_val})"]))

        if not bottom.empty:
            bottom_country = bottom.iloc[0]["Country"]
            bottom_val = bottom.iloc[0].get(metric)
            bullets.append(html.Li([html.B("Lowest: "), f"{bottom_country} ({bottom_val})"]))

        bullets.append(html.Li([html.B("Top 3: "), ", ".join(top["Country"].tolist())]))
        bullets.append(html.Li([html.B("Bottom 3: "), ", ".join(bottom["Country"].tolist())]))

        parts = html.Ul(bullets, className="insights-list")
        return kpis, parts


    # ------------------------------------------------------------
    # Data tab – filtered table
    # ------------------------------------------------------------
    @app.callback(
        Output("data-table", "columns"),
        Output("data-table", "data"),
        Input("metric-selector", "value"),
        Input("continent-filter", "value"),
        Input("development-filter", "value"),
        prevent_initial_call=False,
    )
    def update_data_table(metric, continents, dev_levels):
        if not metric:
            metric = _get_default_metric()
            if not metric:
                return [], []

        df_filtered = merged_data.copy()
        if continents:
            df_filtered = df_filtered[df_filtered["Continent"].isin(continents)]
        if dev_levels:
            df_filtered = df_filtered[df_filtered["Development_Level"].isin(dev_levels)]

        base_cols = ["Country", "Continent", "Development_Level"]
        extra_cols = []
        if "Real_GDP_per_Capita_USD" in df_filtered.columns and metric != "Real_GDP_per_Capita_USD":
            extra_cols.append("Real_GDP_per_Capita_USD")
        cols = base_cols + [metric] + extra_cols
        cols = [c for c in cols if c in df_filtered.columns]

        view = df_filtered[cols].copy()
        # keep it reasonable for the table; users can sort/filter
        view = view.sort_values(metric, ascending=False, na_position="last")
        view = view.head(500)

        columns = [{"name": c.replace("_", " "), "id": c} for c in cols]
        data = view.to_dict("records")
        return columns, data


    # ------------------------------------------------------------
    # Multiple coordinated views: map click -> store selection
    # ------------------------------------------------------------
    @app.callback(
        Output("selected-country", "data"),
        Output("selected-countries", "data"),
        Input("main-visualization", "clickData"),
        State("selected-countries", "data"),
        prevent_initial_call=True,
    )
    def store_selected_country(click_data, selected_countries):
        if not click_data:
            raise PreventUpdate

        # Plotly Choropleth provides 'text' for the clicked country
        try:
            country = click_data["points"][0].get("text")
        except Exception:
            country = None

        if not country:
            raise PreventUpdate

        selected_countries = selected_countries or []
        if country not in selected_countries:
            selected_countries = (selected_countries + [country])[-5:]  # keep it small

        return country, selected_countries



    @app.callback(
        Output("countries-selector", "value"),
        Input("selected-countries", "data"),
        State("countries-selector", "value"),
        prevent_initial_call=True,
    )
    def sync_comparison_countries(selected_countries, current_value):
        """Keep comparison selector in sync with map-based selection."""
        if not selected_countries:
            return no_update
        return selected_countries


    # ------------------------------------------------------------
    # Details-on-demand panel
    # ------------------------------------------------------------
    @app.callback(
        Output("details-text", "children"),
        Output("details-table", "children"),
        Output("details-kpis", "children"),
        Output("details-mini-chart", "figure"),
        Input("selected-country", "data"),
        Input("metric-selector", "value"),
        Input("ui-theme", "data"),
        prevent_initial_call=False,
    )
    def update_details_panel(selected_country, metric, theme):
        if not selected_country:
            return (
                "Click a country in the map to see its values and quick comparisons.",
                None,
                None,
                _safe_figure("Select a country on the map", theme, height=220),
            )

        try:
            row = merged_data.loc[merged_data["Country"] == selected_country]
            if row.empty:
                return f"No data found for {selected_country}.", None, None, _safe_figure("No data found.", theme, height=220)
            row = row.iloc[0]
        except Exception:
            logger.exception("details panel failed to find country=%s", selected_country)
            return "Unable to load details for selected country.", None, None, _safe_figure("Unable to load details.", theme, height=220)

        # Show the current main metric + a couple of helpful metadata fields
        parts = [
            html.Div([html.B("Country: "), row.get("Country", selected_country)]),
        ]
        if "Continent" in merged_data.columns:
            parts.append(html.Div([html.B("Continent: "), row.get("Continent", "-")]))
        if "Development_Level" in merged_data.columns:
            parts.append(html.Div([html.B("Development level: "), row.get("Development_Level", "-")]))

        metric_val = None
        if metric and metric in merged_data.columns:
            metric_val = row.get(metric, None)
            parts.append(html.Div([html.B(f"{metric.replace('_',' ').title()}: "), f"{metric_val}"]))

        # KPI chips
        def _chip(label, value, tone="primary"):
            return dbc.Badge(
                [html.Span(label + ": ", className="chip-label"), html.Span(str(value), className="chip-value")],
                color=tone,
                className="detail-chip",
                pill=True,
            )

        chips = []
        if metric:
            chips.append(_chip("Metric", metric.replace("_", " "), "info"))
        if metric_val is not None:
            chips.append(_chip("Value", metric_val, "primary"))
        if "Real_GDP_per_Capita_USD" in merged_data.columns:
            gdp = row.get("Real_GDP_per_Capita_USD", None)
            if gdp is not None and gdp == gdp:
                chips.append(_chip("GDP/Cap", f"${float(gdp):,.0f}", "success"))
        if "Total_Population" in merged_data.columns:
            pop = row.get("Total_Population", None)
            if pop is not None and pop == pop:
                chips.append(_chip("Pop", f"{float(pop)/1e6:.1f}M", "secondary"))

        kpi_row = html.Div(chips, className="details-kpis-row")

        table = dbc.ListGroup([dbc.ListGroupItem(p) for p in parts])

        # Mini contextual chart: selected vs continent mean vs global mean
        fig = go.Figure()
        try:
            global_mean = None
            cont_mean = None
            if metric and metric in merged_data.columns:
                df_valid = merged_data.dropna(subset=["Country", metric]).copy()
                global_mean = float(df_valid[metric].mean()) if not df_valid.empty else None

                cont = row.get("Continent", None)
                if cont and "Continent" in df_valid.columns:
                    cont_df = df_valid[df_valid["Continent"] == cont]
                    if not cont_df.empty:
                        cont_mean = float(cont_df[metric].mean())

            bars_x = []
            bars_y = []
            if metric_val is not None and metric_val == metric_val:
                bars_x.append("Selected")
                bars_y.append(float(metric_val))
            if cont_mean is not None:
                bars_x.append("Continent avg")
                bars_y.append(cont_mean)
            if global_mean is not None:
                bars_x.append("Global avg")
                bars_y.append(global_mean)

            fig.add_trace(
                go.Bar(
                    x=bars_x,
                    y=bars_y,
                    marker=dict(color=["rgba(255,107,107,0.92)"] + ["rgba(33,150,243,0.75)"] * (len(bars_x) - 1)),
                    hovertemplate="%{x}<br>%{y:,.2f}<extra></extra>",
                )
            )

            fig.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
                height=220,
                title=dict(text=(metric or "").replace("_", " "), x=0.01, xanchor="left"),
            )
        except Exception:
            logger.exception("details mini chart failed for country=%s metric=%s", selected_country, metric)
            fig = _safe_figure("Unable to render mini chart.", theme, height=220)

        fig = viz_factory.apply_theme(fig, theme) if isinstance(fig, go.Figure) else fig

        return f"Selected: {selected_country}", table, kpi_row, fig


    # ------------------------------------------------------------
    # Statistical value idioms: distribution view
    # ------------------------------------------------------------
    @app.callback(
        Output("distribution-chart", "figure"),
        Input("distribution-metric", "value"),
        Input("distribution-idiom", "value"),
        Input("distribution-bins", "value"),
        Input("distribution-show-points", "value"),
        Input("continent-filter", "value"),
        Input("development-filter", "value"),
        Input("selected-country", "data"),
        Input("ui-theme", "data"),
        prevent_initial_call=False,
    )
    def update_distribution(metric, idiom, bins, show_points, continents, dev_levels, selected_country, theme):
        if not metric:
            metric = _get_default_metric()
            if not metric:
                return _safe_figure("No metric available", theme, height=380)

        try:
            df_filtered = _apply_filters(merged_data.copy(), continents, dev_levels)
            fig = viz_factory.create_distribution_chart(
                df=df_filtered,
                metric=metric,
                idiom=idiom or "hist",
                bins=int(bins or 20),
                show_points=("show" in (show_points or [])),
                group_by="Continent" if "Continent" in df_filtered.columns else None,
                selected_country=selected_country,
            )
            return viz_factory.apply_theme(fig, theme)
        except Exception:
            logger.exception("distribution-chart failed for metric=%s", metric)
            return _safe_figure("Unable to render distribution for this metric.", theme, height=380)
