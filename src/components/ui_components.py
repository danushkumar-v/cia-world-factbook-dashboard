"""
Global Insights Explorer - UI Components
Reusable Dash components for the application
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd



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
    """Create summary statistics cards with clear labels."""
    total_countries = merged_data["Country"].dropna().nunique()

    # Defensive: ignore obviously non-positive values
    gdp_series = merged_data.get("Real_GDP_per_Capita_USD")
    if gdp_series is not None:
        gdp_clean = gdp_series[gdp_series > 0]
        avg_gdp = gdp_clean.mean()
    else:
        avg_gdp = None

    total_population = merged_data.get("Total_Population", pd.Series(dtype=float)).sum()
    internet_series = merged_data.get("internet_users_total", pd.Series(dtype=float))
    total_internet_users = internet_series.sum()

    return dbc.Row(
        [
            dbc.Col(
                create_stat_card("🌍", f"{total_countries}", "Countries & Territories"),
                width=12,
                lg=3,
                className="mb-3",
            ),
            dbc.Col(
                create_stat_card(
                    "💰",
                    "N/A" if avg_gdp is None else f"${avg_gdp:,.0f}",
                    "Avg GDP per Capita",
                ),
                width=12,
                lg=3,
                className="mb-3",
            ),
            dbc.Col(
                create_stat_card(
                    "👥",
                    f"{total_population/1e9:.2f}B",
                    "Total Population",
                ),
                width=12,
                lg=3,
                className="mb-3",
            ),
            dbc.Col(
                create_stat_card(
                    "🌐",
                    f"{total_internet_users/1e9:.2f}B",
                    "Internet Users",
                ),
                width=12,
                lg=3,
                className="mb-3",
            ),
        ],
        className="mb-4",
    )

def create_filters_panel(metrics_info):
    """Create advanced filters panel (overview → filter → details)."""
    categories = list(metrics_info.keys())
    default_domain = categories[0] if categories else None

    return html.Div(
        [
            html.H4(
                "🎛️ Control Panel",
                style={
                    "marginBottom": "1.5rem",
                    "fontFamily": "Outfit, Inter, sans-serif",
                    "color": "#1a2332",
                },
            ),

            # Domain & metric selection
            html.Div(
                [
                    html.Label("Data Domain", className="control-label"),
                    dcc.Dropdown(
                        id="domain-selector",
                        options=[{"label": cat, "value": cat} for cat in categories],
                        value=default_domain,
                        clearable=False,
                        className="mb-3",
                    ),

                    html.Label("Metric", className="control-label"),
                    dcc.Dropdown(
                        id="metric-selector",
                        clearable=False,
                        className="mb-3",
                    ),
                ],
                className="control-group",
            ),

            # Visualization settings
            html.Div(
                [
                    html.Label("Visualization Type", className="control-label"),
                    dcc.Dropdown(
                        id="viz-type-selector",
                        options=[
                            {"label": "🗺️ Choropleth Map", "value": "choropleth"},
                            {"label": "📊 Regional Bars", "value": "regional"},
                            {"label": "☀️ Sunburst (Hierarchy)", "value": "sunburst"},
                            {"label": "🌐 Globe (optional)", "value": "globe"},
                        ],
                        value="choropleth",  # 2D as default – no unjustified 3D
                        clearable=False,
                        className="mb-3",
                    ),

                    html.Label("Color Scheme", className="control-label"),
                    dcc.Dropdown(
                        id="color-scheme-selector",
                        options=[
                            {"label": "Viridis (default)", "value": "Viridis"},
                            {"label": "Blues", "value": "Blues"},
                            {"label": "Reds", "value": "Reds"},
                            {"label": "Greens", "value": "Greens"},
                            {"label": "Plasma", "value": "Plasma"},
                            {"label": "Inferno", "value": "Inferno"},
                            # Rainbow is allowed but not default
                            {"label": "Rainbow (discouraged)", "value": "Rainbow"},
                        ],
                        value="Viridis",
                        clearable=False,
                        className="mb-3",
                    ),
                ],
                className="control-group",
            ),

            # Filters
            html.Div(
                [
                    html.Label("Filter by Continent", className="control-label"),
                    dcc.Dropdown(
                        id="continent-filter",
                        options=[],  # can be filled in a callback
                        multi=True,
                        placeholder="All Continents",
                        className="mb-3",
                    ),

                    html.Label("Filter by Development Level", className="control-label"),
                    dcc.Dropdown(
                        id="development-filter",
                        options=[],
                        multi=True,
                        placeholder="All Levels",
                        className="mb-3",
                    ),
                ],
                className="control-group",
            ),

            html.Hr(style={"margin": "1.5rem 0"}),

            html.Button(
                "🔄 Refresh Visualization",
                id="apply-filters-btn",
                className="btn-custom-primary w-100",
            ),
        ],
        className="filters-sidebar",
    )


def create_comparison_panel(country_list):
    """Create country comparison panel."""
    return html.Div(
        [
            html.H4(
                "🔍 Country Comparison",
                style={
                    "marginBottom": "1.5rem",
                    "fontFamily": "Outfit, Inter, sans-serif",
                },
            ),
            html.Div(
                [
                    html.Label("Select Countries (2–6)", className="control-label"),
                    dcc.Dropdown(
                        id="countries-selector",
                        options=[{"label": c, "value": c} for c in country_list],
                        multi=True,
                        placeholder="Select countries to compare…",
                        className="mb-3",
                    ),
                    html.Label("Metric", className="control-label"),
                    dcc.Dropdown(
                        id="comparison-metric-selector",
                        clearable=False,
                        className="mb-3",
                    ),
                    html.Label("Chart Type", className="control-label"),
                    dcc.Dropdown(
                        id="comparison-chart-type",
                        options=[
                            {"label": "Bar Chart", "value": "bar"},
                            {"label": "Radar (Spider)", "value": "radar"},
                        ],
                        value="bar",
                        clearable=False,
                        className="mb-3",
                    ),
                ],
                className="control-group",
            ),
            html.Button(
                "Compare Countries",
                id="compare-btn",
                className="btn-custom-primary w-100",
            ),
        ],
        className="controls-panel",
    )


def create_correlation_panel():
    """Create correlation analysis panel (overview + detailed scatter)."""
    return html.Div(
        [
            html.H4(
                "📈 Correlation Explorer",
                style={
                    "marginBottom": "1.5rem",
                    "fontFamily": "Outfit, Inter, sans-serif",
                },
            ),

            html.Div(
                [
                    html.Label("X-Axis Metric", className="control-label"),
                    dcc.Dropdown(
                        id="correlation-x-selector",
                        clearable=False,
                        className="mb-3",
                    ),
                    html.Label("Y-Axis Metric", className="control-label"),
                    dcc.Dropdown(
                        id="correlation-y-selector",
                        clearable=False,
                        className="mb-3",
                    ),
                ],
                className="control-group",
            ),

            html.Div(
                [
                    html.Label("Color By (optional)", className="control-label"),
                    dcc.Dropdown(
                        id="correlation-color-selector",
                        placeholder="e.g. Continent or Development Level",
                        clearable=True,
                        className="mb-3",
                    ),
                    html.Label("Group By (for small multiples)", className="control-label"),
                    dcc.Dropdown(
                        id="correlation-groupby-selector",
                        options=[
                            {"label": "None", "value": "None"},
                            {"label": "Continent", "value": "Continent"},
                            {"label": "Development Level", "value": "Development_Level"},
                        ],
                        value="Continent",
                        clearable=False,
                        className="mb-3",
                    ),
                ],
                className="control-group",
            ),

            html.Button(
                "Generate Scatter Plot",
                id="correlation-btn",
                className="btn-custom-primary w-100",
            ),
        ],
        className="controls-panel",
    )


def create_distribution_panel(metrics_info):
    """Create distribution analysis controls.

    Aligns with the course emphasis on *statistical value idioms* by letting
    users choose an idiom (histogram/box/violin) and adjust key parameters
    like histogram binning.
    """

    # metrics_info here is a dict: category -> list[{name,label,...}]
    flat_metrics = []
    for cat, mets in (metrics_info or {}).items():
        for m in mets:
            flat_metrics.append(
                {
                    "label": f"{cat}: {m.get('label', m.get('name'))}",
                    "value": m.get("name"),
                }
            )

    return html.Div(
        [
            html.H4(
                "📊 Distribution",
                style={
                    "marginBottom": "1.5rem",
                    "fontFamily": "Outfit, Inter, sans-serif",
                },
            ),

            html.Div(
                [
                    html.Label("Metric", className="control-label"),
                    dcc.Dropdown(
                        id="distribution-metric",
                        options=flat_metrics,
                        value=flat_metrics[0]["value"] if flat_metrics else None,
                        clearable=False,
                        className="mb-3",
                    ),
                    html.Label("Idiom", className="control-label"),
                    dcc.Dropdown(
                        id="distribution-idiom",
                        options=[
                            {"label": "Histogram (frequency)", "value": "hist"},
                            {"label": "Box plot (summary)", "value": "box"},
                            {"label": "Violin (density + summary)", "value": "violin"},
                        ],
                        value="hist",
                        clearable=False,
                        className="mb-3",
                    ),
                    html.Label("Histogram bins", className="control-label"),
                    dcc.Slider(
                        id="distribution-bins",
                        min=5,
                        max=60,
                        step=1,
                        value=20,
                        marks={5: "5", 20: "20", 40: "40", 60: "60"},
                    ),
                    html.Div(style={"height": "0.75rem"}),
                    dbc.Checklist(
                        id="distribution-show-points",
                        options=[{"label": "Show individual data points (when applicable)", "value": "show"}],
                        value=[],
                        switch=True,
                        className="mb-3",
                    ),
                ],
                className="control-group",
            ),

            html.Button(
                "Generate Distribution",
                id="distribution-btn",
                className="btn-custom-primary w-100",
            ),
        ],
        className="controls-panel",
    )


def create_details_panel():
    """A small details-on-demand panel that updates on selection."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Details on demand", className="card-title"),
                html.Div(
                    "Click a country in the map to see its values and quick comparisons.",
                    id="details-text",
                    className="text-muted",
                ),
                html.Hr(),
                html.Div(id="details-table"),
            ]
        ),
        className="shadow-sm",
    )
