"""
Application Callbacks
All Dash callbacks for interactivity
"""
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go


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
        Output('comparison-metrics-selector', 'options'),
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
        Input('apply-filters-btn', 'n_clicks'),
        State('metric-selector', 'value'),
        State('viz-type-selector', 'value'),
        State('color-scheme-selector', 'value'),
        State('continent-filter', 'value'),
        State('development-filter', 'value')
    )
    def update_main_visualization(n_clicks, metric, viz_type, color_scheme, continents, dev_levels):
        """Update main visualization"""
        if not metric:
            raise PreventUpdate
        
        df_filtered = merged_data.copy()
        
        if continents:
            df_filtered = df_filtered[df_filtered['Continent'].isin(continents)]
        
        if dev_levels:
            df_filtered = df_filtered[df_filtered['Development_Level'].isin(dev_levels)]
        
        title = f"{metric.replace('_', ' ').title()} - Global Distribution"
        
        if viz_type == 'choropleth':
            return viz_factory.create_choropleth_map(df_filtered, metric, title, color_scheme)
        elif viz_type == 'globe':
            return viz_factory.create_3d_globe(df_filtered, metric, title)
        elif viz_type == 'sunburst':
            return viz_factory.create_sunburst_chart(df_filtered, metric)
        elif viz_type == 'regional':
            return viz_factory.create_regional_bar_chart(df_filtered, metric)
        
        return viz_factory.create_choropleth_map(df_filtered, metric, title, color_scheme)

    @app.callback(
        Output('comparison-chart', 'figure'),
        Input('compare-btn', 'n_clicks'),
        State('countries-selector', 'value'),
        State('comparison-metrics-selector', 'value'),
        State('comparison-chart-type', 'value')
    )
    def update_comparison_chart(n_clicks, countries, metrics, chart_type):
        """Update country comparison chart"""
        if not countries or not metrics or len(countries) < 2:
            return go.Figure().add_annotation(
                text="Please select at least 2 countries and metrics to compare",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
        
        if chart_type == 'radar':
            return viz_factory.create_comparison_radar(merged_data, countries, metrics)
        
        return go.Figure()

    @app.callback(
        Output('correlation-chart', 'figure'),
        Input('correlation-btn', 'n_clicks'),
        State('correlation-x-selector', 'value'),
        State('correlation-y-selector', 'value'),
        State('correlation-color-selector', 'value')
    )
    def update_correlation_chart(n_clicks, x_metric, y_metric, color_by):
        """Update correlation scatter plot"""
        if not x_metric or not y_metric:
            raise PreventUpdate
        
        return viz_factory.create_scatter_correlation(merged_data, x_metric, y_metric, color_by)

    @app.callback(
        Output('regional-chart', 'figure'),
        Input('metric-selector', 'value')
    )
    def update_regional_chart(metric):
        """Update regional comparison chart"""
        if not metric:
            raise PreventUpdate
        
        return viz_factory.create_regional_bar_chart(merged_data, metric, 'mean')
