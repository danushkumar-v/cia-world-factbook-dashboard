"""
Global Insights Explorer - UI Components
Reusable Dash components for the application
"""
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_navbar():
    """Create navigation bar"""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("🌍", style={'fontSize': '2rem', 'marginRight': '0.75rem'}),
                        html.Span("Global Insights Explorer", className="navbar-brand")
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], width='auto'),
            ], align='center', className='g-0'),
            dbc.Row([
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("🗺️ Maps", href="#", className="nav-link-custom", id='nav-maps')),
                        dbc.NavItem(dbc.NavLink("📊 Analytics", href="#", className="nav-link-custom", id='nav-analytics')),
                        dbc.NavItem(dbc.NavLink("🔍 Compare", href="#", className="nav-link-custom", id='nav-compare')),
                        dbc.NavItem(dbc.NavLink("📈 Trends", href="#", className="nav-link-custom", id='nav-trends')),
                    ], navbar=True)
                ])
            ], className='ms-auto')
        ], fluid=True),
        className="navbar-custom",
        dark=True
    )


def create_stat_card(icon, value, label, color="primary"):
    """Create a statistics card"""
    return html.Div([
        html.Div(icon, style={'fontSize': '2.5rem', 'marginBottom': '0.5rem'}),
        html.Div(value, className="stat-value"),
        html.Div(label, className="stat-label"),
    ], className="stat-card")


def create_stats_cards(merged_data):
    """Create summary statistics cards"""
    total_countries = len(merged_data['Country'].dropna())
    avg_gdp = merged_data['Real_GDP_per_Capita_USD'].mean()
    total_population = merged_data['Total_Population'].sum()
    avg_internet = merged_data['internet_users_total'].sum()
    
    return dbc.Row([
        dbc.Col([
            create_stat_card("🌍", f"{total_countries}", "Countries")
        ], width=12, lg=3, className="mb-3"),
        
        dbc.Col([
            create_stat_card("💰", f"${avg_gdp:,.0f}", "Avg GDP per Capita")
        ], width=12, lg=3, className="mb-3"),
        
        dbc.Col([
            create_stat_card("👥", f"{total_population/1e9:.2f}B", "Total Population")
        ], width=12, lg=3, className="mb-3"),
        
        dbc.Col([
            create_stat_card("🌐", f"{avg_internet/1e9:.2f}B", "Internet Users")
        ], width=12, lg=3, className="mb-3"),
    ], className="mb-4")


def create_filters_panel(metrics_info):
    """Create advanced filters panel"""
    categories = list(metrics_info.keys())
    
    return html.Div([
        html.H4("🎛️ Control Panel", style={
            'marginBottom': '1.5rem',
            'fontFamily': 'Outfit, Inter, sans-serif',
            'color': '#1a2332'
        }),
        
        html.Div([
            html.Label("Data Domain", className="control-label"),
            dcc.Dropdown(
                id='domain-selector',
                options=[{'label': cat, 'value': cat} for cat in categories],
                value='Economy',
                clearable=False,
                className='mb-3'
            )
        ], className="control-group"),
        
        html.Div([
            html.Label("Metric", className="control-label"),
            dcc.Dropdown(
                id='metric-selector',
                clearable=False,
                className='mb-3'
            )
        ], className="control-group"),
        
        html.Div([
            html.Label("Visualization Type", className="control-label"),
            dcc.Dropdown(
                id='viz-type-selector',
                options=[
                    {'label': '🗺️ Choropleth Map', 'value': 'choropleth'},
                    {'label': '🌐 3D Globe', 'value': 'globe'},
                    {'label': '☀️ Sunburst Chart', 'value': 'sunburst'},
                    {'label': '📊 Regional Bars', 'value': 'regional'}
                ],
                value='choropleth',
                clearable=False,
                className='mb-3'
            )
        ], className="control-group"),
        
        html.Div([
            html.Label("Color Scheme", className="control-label"),
            dcc.Dropdown(
                id='color-scheme-selector',
                options=[
                    {'label': 'Blues', 'value': 'Blues'},
                    {'label': 'Reds', 'value': 'Reds'},
                    {'label': 'Greens', 'value': 'Greens'},
                    {'label': 'Viridis', 'value': 'Viridis'},
                    {'label': 'Plasma', 'value': 'Plasma'},
                    {'label': 'Inferno', 'value': 'Inferno'},
                    {'label': 'Rainbow', 'value': 'Rainbow'},
                ],
                value='Blues',
                clearable=False,
                className='mb-3'
            )
        ], className="control-group"),
        
        html.Div([
            html.Label("Filter by Continent", className="control-label"),
            dcc.Dropdown(
                id='continent-filter',
                multi=True,
                placeholder="All Continents",
                className='mb-3'
            )
        ], className="control-group"),
        
        html.Div([
            html.Label("Development Level", className="control-label"),
            dcc.Dropdown(
                id='development-filter',
                multi=True,
                placeholder="All Levels",
                className='mb-3'
            )
        ], className="control-group"),
        
        html.Hr(style={'margin': '1.5rem 0'}),
        
        html.Button(
            "🔄 Refresh Visualization",
            id='apply-filters-btn',
            className='btn-custom-primary w-100'
        )
        
    ], className="filters-sidebar")


def create_comparison_panel(country_list):
    """Create country comparison panel"""
    return html.Div([
        html.H4("🔍 Country Comparison", style={
            'marginBottom': '1.5rem',
            'fontFamily': 'Outfit, Inter, sans-serif'
        }),
        
        html.Div([
            html.Label("Select Countries (2-6)", className="control-label"),
            dcc.Dropdown(
                id='countries-selector',
                options=[{'label': country, 'value': country} for country in country_list],
                multi=True,
                placeholder="Select countries to compare...",
                className='mb-3'
            )
        ]),
        
        html.Div([
            html.Label("Comparison Metrics", className="control-label"),
            dcc.Dropdown(
                id='comparison-metrics-selector',
                multi=True,
                placeholder="Select metrics to compare...",
                className='mb-3'
            )
        ]),
        
        html.Div([
            html.Label("Chart Type", className="control-label"),
            dcc.Dropdown(
                id='comparison-chart-type',
                options=[
                    {'label': '🕸️ Radar Chart', 'value': 'radar'},
                    {'label': '📊 Bar Chart', 'value': 'bar'},
                    {'label': '📈 Line Chart', 'value': 'line'}
                ],
                value='radar',
                clearable=False,
                className='mb-3'
            )
        ]),
        
        html.Button(
            "Compare Countries",
            id='compare-btn',
            className='btn-custom-primary w-100'
        )
    ], className="controls-panel")


def create_correlation_panel():
    """Create correlation analysis panel"""
    return html.Div([
        html.H4("📈 Correlation Explorer", style={
            'marginBottom': '1.5rem',
            'fontFamily': 'Outfit, Inter, sans-serif'
        }),
        
        html.Div([
            html.Label("X-Axis Metric", className="control-label"),
            dcc.Dropdown(
                id='correlation-x-selector',
                clearable=False,
                className='mb-3'
            )
        ]),
        
        html.Div([
            html.Label("Y-Axis Metric", className="control-label"),
            dcc.Dropdown(
                id='correlation-y-selector',
                clearable=False,
                className='mb-3'
            )
        ]),
        
        html.Div([
            html.Label("Color By", className="control-label"),
            dcc.Dropdown(
                id='correlation-color-selector',
                options=[
                    {'label': 'Continent', 'value': 'Continent'},
                    {'label': 'Development Level', 'value': 'Development_Level'}
                ],
                value='Continent',
                clearable=False,
                className='mb-3'
            )
        ]),
        
        html.Button(
            "Generate Scatter Plot",
            id='correlation-btn',
            className='btn-custom-primary w-100'
        )
    ], className="controls-panel")
