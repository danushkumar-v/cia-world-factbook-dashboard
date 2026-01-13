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
import pandas as pd


def register_callbacks(app, merged_data, metrics_info, viz_factory):
    """Register all application callbacks"""
    
    @app.callback(
        Output('metric-selector', 'options'),
        Output('metric-selector', 'value'),
        Input('domain-selector', 'value')
    )
    def update_metric_options(domain):
        """Update metric options based on selected domain"""
        if domain and domain in metrics_info:
            metrics = metrics_info[domain]
            options = [{'label': m['label'], 'value': m['name']} for m in metrics]
            default_value = metrics[0]['name'] if metrics else None
            return options, default_value
        return [], None

    @app.callback(
        Output('comparison-metric-selector', 'options'),
        Input('domain-selector', 'value')
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
        Input('domain-selector', 'value')
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
        Input('domain-selector', 'value')
    )
    def update_filter_options(domain):
        """Update filter dropdown options"""
        continents = sorted(merged_data['Continent'].unique())
        continents = [c for c in continents if c != 'Other']
        continent_options = [{'label': cont, 'value': cont} for cont in continents]
        
        dev_levels = merged_data['Development_Level'].dropna().unique()
        dev_options = [{'label': level, 'value': level} for level in dev_levels]
        
        return continent_options, dev_options

    @app.callback(
        Output('main-visualization', 'figure'),
        Input("main-visualization", "hoverData"),  # ✅ added
        Input('apply-filters-btn', 'n_clicks'),  # ✅ keep
        State('metric-selector', 'value'),
        State('viz-type-selector', 'value'),
        State('color-scheme-selector', 'value'),
        State('continent-filter', 'value'),
        State('development-filter', 'value')
    )
    def update_main_visualization(hoverData, n_clicks, metric, viz_type, color_scheme, continents, dev_levels):
        """Update main visualization + hover 'enlarge' effect for choropleth"""

        if not metric:
            raise PreventUpdate

        df_filtered = merged_data.copy()

        if continents:
            df_filtered = df_filtered[df_filtered['Continent'].isin(continents)]

        if dev_levels:
            df_filtered = df_filtered[df_filtered['Development_Level'].isin(dev_levels)]

        title = f"{metric.replace('_', ' ').title()} - Global Distribution"

        # ---- Build the base figure (your normal behavior) ----
        if viz_type == 'choropleth':
            fig = viz_factory.create_choropleth_map(df_filtered, metric, title, color_scheme)

            # ---- Hover "enlarge" effect (only for choropleth) ----
            if hoverData and "points" in hoverData and len(hoverData["points"]) > 0:
                # For choropleth, 'location' is the country identifier (you use locationmode='country names')
                country = hoverData["points"][0].get("location") or hoverData["points"][0].get("text")

                if country:
                    # Overlay trace: thick outline + subtle fill -> looks like enlargement/pop-out
                    fig.add_trace(
                        go.Choropleth(
                            locations=[country],
                            z=[1],
                            locationmode="country names",  # matches your base choropleth
                            colorscale=[[0, "rgba(255,255,255,0.18)"], [1, "rgba(255,255,255,0.18)"]],
                            showscale=False,
                            hoverinfo="skip",
                            marker_line_color="black",
                            marker_line_width=6,
                            zmin=0,
                            zmax=1,
                        )
                    )

            return fig

        elif viz_type == 'globe':
            return viz_factory.create_3d_globe(df_filtered, metric, title)

        elif viz_type == 'sunburst':
            return viz_factory.create_sunburst_chart(df_filtered, metric)

        elif viz_type == 'regional':
            return viz_factory.create_regional_bar_chart(df_filtered, metric)

        # fallback
        return viz_factory.create_choropleth_map(df_filtered, metric, title, color_scheme)

    @app.callback(
        Output("hover-overlay", "figure"),
        Input("main-visualization", "hoverData"),
        State("viz-type-selector", "value"),
    )
    def hover_outline(hoverData, viz_type):

        # Transparent empty overlay when not hovering
        if viz_type != "choropleth" or not hoverData or "points" not in hoverData:
            fig = go.Figure()
            fig.update_layout(
                geo=dict(
                    projection_type="natural earth",
                    showframe=False,
                    showcoastlines=False,
                    bgcolor="rgba(0,0,0,0)"
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=0, b=0),
            )
            return fig

        # ✅ USE TEXT (country name) — NOT location
        country = hoverData["points"][0].get("text")
        if not country:
            raise PreventUpdate

        fig = go.Figure(
            go.Choropleth(
                locations=[country],
                locationmode="country names",  # ✅ MATCH BASE MAP
                z=[1],
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                showscale=False,
                hoverinfo="skip",
                marker_line_color="black",
                marker_line_width=5,  # 🔥 bold outline
            )
        )

        fig.update_layout(
            geo=dict(
                projection_type="natural earth",
                showframe=False,
                showcoastlines=False,
                bgcolor="rgba(0,0,0,0)"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
        )

        return fig

    @app.callback(
        Output('comparison-chart', 'figure'),
        Input('compare-btn', 'n_clicks'),
        State('countries-selector', 'value'),
        State('comparison-metric-selector', 'value'),
        State('comparison-chart-type', 'value')
    )
    def update_comparison_chart(n_clicks, countries, metrics, chart_type):
        """Update country comparison chart"""

        # Normalize metric input: allow string or list
        if isinstance(metrics, list):
            if len(metrics) == 0:
                metrics = None
            else:
                metric = metrics[0]  # take the first metric
        else:
            metric = metrics

        if not countries or not metric or len(countries) < 2:
            return go.Figure().add_annotation(
                text="Please select at least 2 countries and 1 metric to compare",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )

        if chart_type == "radar":
            return viz_factory.create_comparison_radar(merged_data, countries, metric)

        elif chart_type == "bar":
            return viz_factory.create_comparison_bar(merged_data, countries, metric)

        else:
            return go.Figure().add_annotation(
                text="Unknown chart type selected",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )

    @app.callback(
        Output('correlation-chart', 'figure'),
        Output('heatmap-chart', 'figure'),
        Input('correlation-btn', 'n_clicks'),
        State('correlation-x-selector', 'value'),
        State('correlation-y-selector', 'value'),
        State('correlation-color-selector', 'value')
    )
    def update_correlation_chart(n_clicks, x_metric, y_metric, color_by):
        """Update correlation scatter plot"""
        if not x_metric or not y_metric:
            raise PreventUpdate

        scatter_fig = viz_factory.create_scatter_correlation(merged_data, x_metric, y_metric)
        heatmap_fig = viz_factory.create_heatmap_correlation(merged_data, metrics=[x_metric, y_metric])
        return scatter_fig, heatmap_fig

    @app.callback(
        Output('regional-chart', 'figure'),
        Input('metric-selector', 'value')
    )
    def update_regional_chart(metric):
        """Update regional comparison chart"""
        if not metric:
            raise PreventUpdate
        
        return viz_factory.create_regional_bar_chart(merged_data, metric, 'mean')


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
    )
    def sync_comparison_countries(selected_countries, current_value):
        """Keep comparison selector in sync with map-based selection."""
        if not selected_countries:
            return current_value
        return selected_countries


    # ------------------------------------------------------------
    # Details-on-demand panel
    # ------------------------------------------------------------
    @app.callback(
        Output("details-text", "children"),
        Output("details-table", "children"),
        Input("selected-country", "data"),
        State("metric-selector", "value"),
    )
    def update_details_panel(selected_country, metric):
        if not selected_country:
            return (
                "Click a country in the map to see its values and quick comparisons.",
                None,
            )

        row = merged_data.loc[merged_data["Country"] == selected_country]
        if row.empty:
            return f"No data found for {selected_country}.", None

        row = row.iloc[0]

        # Show the current main metric + a couple of helpful metadata fields
        parts = [
            html.Div([html.B("Country: "), row.get("Country", selected_country)]),
            html.Div([html.B("Continent: "), row.get("Continent", "-")]),
            html.Div([html.B("Development level: "), row.get("Development_Level", "-")]),
        ]

        if metric and metric in merged_data.columns:
            val = row.get(metric, None)
            parts.append(html.Div([html.B(f"{metric.replace('_',' ').title()}: "), f"{val}" ]))

        table = dbc.ListGroup([dbc.ListGroupItem(p) for p in parts])
        return f"Selected: {selected_country}", table


    # ------------------------------------------------------------
    # Statistical value idioms: distribution view
    # ------------------------------------------------------------
    @app.callback(
        Output("distribution-chart", "figure"),
        Input("distribution-btn", "n_clicks"),
        State("distribution-metric", "value"),
        State("distribution-idiom", "value"),
        State("distribution-bins", "value"),
        State("distribution-show-points", "value"),
        State("continent-filter", "value"),
        State("development-filter", "value"),
        State("selected-country", "data"),
    )
    def update_distribution(n_clicks, metric, idiom, bins, show_points, continents, dev_levels, selected_country):
        if not metric:
            raise PreventUpdate

        df_filtered = merged_data.copy()
        if continents:
            df_filtered = df_filtered[df_filtered["Continent"].isin(continents)]
        if dev_levels:
            df_filtered = df_filtered[df_filtered["Development_Level"].isin(dev_levels)]

        return viz_factory.create_distribution_chart(
            df=df_filtered,
            metric=metric,
            idiom=idiom or "hist",
            bins=int(bins or 20),
            show_points=("show" in (show_points or [])),
            group_by="Continent",
            selected_country=selected_country,
        )
