"""
Application Layout
Main layout structure for the Dash application
"""
from dash import html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


from src.components.ui_components import (
    create_navbar,
    create_stats_cards,
    create_filters_panel,
    create_comparison_panel,
    create_correlation_panel,
    create_distribution_panel,
    create_details_panel,
)


def create_layout(merged_data, metrics_info, country_list):
    """Create the main application layout"""
    
    # Update continent filter options
    continents = sorted(merged_data['Continent'].unique())
    continents = [c for c in continents if c != 'Other']
    
    # Update development level filter options
    dev_levels = merged_data['Development_Level'].dropna().unique()

    # ----------------------------
    # Default figure (choropleth) shown on first load
    # ----------------------------
    # pick a sensible default metric: first metric in the first category
    first_category = next(iter(metrics_info))
    first_item = metrics_info[first_category][0]

    # metrics_info items can be either strings OR dicts like {"label":..., "value":...}
    if isinstance(first_item, dict):
        default_metric = first_item.get("value") or first_item.get("column") or first_item.get("name")
    else:
        default_metric = first_item

    if default_metric not in merged_data.columns:
        # fallback: pick the first numeric column that is not an ID/key column
        key_cols = {"Country", "Country_Name", "Continent", "Development_Level"}
        numeric_cols = [c for c in merged_data.columns if c not in key_cols and
                        str(merged_data[c].dtype) != "object"]
        default_metric = numeric_cols[0] if numeric_cols else merged_data.columns[0]

    hover_col = "Country_Name" if "Country_Name" in merged_data.columns else "Country"

    default_fig = px.choropleth(
        merged_data.dropna(subset=[default_metric]),
        locations="Country",
        color=default_metric,
        hover_name=hover_col,
        color_continuous_scale="Viridis",
        projection="natural earth",
        title=f"{default_metric} (default view)",
    )
    default_fig.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        geo=dict(showframe=False, showcoastlines=False),
    )

    
    return html.Div([
        # Cross-view interaction state (Multiple Views)
        dcc.Store(id="selected-country", data=None),
        dcc.Store(id="selected-countries", data=[]),

        # Navbar
        create_navbar(),
        
        # Main container
        dbc.Container([
            # Statistics cards
            html.Div(create_stats_cards(merged_data), className="mt-4"),
            
            # Main content area
            dbc.Row([
                # Left sidebar - Filters
                dbc.Col([
                    create_filters_panel(metrics_info)
                ], width=12, lg=3, className="mb-4"),
                
                # Main visualization area
                dbc.Col([
                    # Main map/chart
                    html.Div([
                        dcc.Loading(
                            id="loading-main-viz",
                            type="circle",
                            children=[
                                dcc.Graph(
                                    id="hover-overlay",
                                    figure=go.Figure(),
                                    config={'displayModeBar': False, 'displaylogo': False},
                                    style={
                                        "position": "absolute",
                                        "top": "0", "left": "0", "right": "0", "bottom": "0",
                                        "height": "700px",
                                        "pointerEvents": "none"
                                    },
                                ),

                                dcc.Graph(
                                    id='main-visualization',
                                    figure = default_fig,
                                    config={'displayModeBar': True, 'displaylogo': False},
                                    style={'height': '700px'}
                                )
                            ]
                        )
                    ], className="chart-container mb-4"),

                    # Details-on-demand panel (updates when you click a country)
                    html.Div(
                        create_details_panel(),
                        className="mb-4",
                    ),
                    
                    # Tabs for additional analysis
                    dbc.Tabs([
                        dbc.Tab(label="🔍 Compare", tab_id="tab-compare", children=[
                            html.Div([
                                dbc.Row([
                                    dbc.Col([create_comparison_panel(country_list)], width=12, lg=4),
                                    dbc.Col([
                                        dcc.Loading(
                                            id="loading-comparison",
                                            type="circle",
                                            children=[
                                                dcc.Graph(id='comparison-chart')
                                            ]
                                        )
                                    ], width=12, lg=8)
                                ])
                            ], className="p-3")
                        ]),
                        
                        dbc.Tab(label="📈 Correlation", tab_id="tab-correlation", children=[
                            html.Div([
                                dbc.Row([
                                    dbc.Col([create_correlation_panel()], width=12, lg=4),
                                    dbc.Col([
                                        dcc.Loading(
                                            id="loading-correlation",
                                            type="circle",
                                            children=[
                                                html.Div(
                                                    [
                                                        dcc.Graph(
                                                            id='correlation-chart',
                                                            style={'width': '50%', 'display': 'inline-block'}
                                                        ),
                                                        dcc.Graph(
                                                            id='heatmap-chart',
                                                            style={'width': '50%', 'display': 'inline-block'}
                                                        ),
                                                    ]
                                                )
                                            ]
                                        )
                                    ], width=12, lg=8)
                                ])
                            ], className="p-3")
                        ]),
                        
                        dbc.Tab(label="🌍 Regional", tab_id="tab-regional", children=[
                            html.Div([
                                dcc.Loading(
                                    id="loading-regional",
                                    type="circle",
                                    children=[
                                        dcc.Graph(id='regional-chart')
                                    ]
                                )
                            ], className="p-3")
                        ]),

                        dbc.Tab(label="📊 Distribution", tab_id="tab-distribution", children=[
                            html.Div([
                                dbc.Row([
                                    dbc.Col([create_distribution_panel(metrics_info)], width=12, lg=4),
                                    dbc.Col([
                                        dcc.Loading(
                                            id="loading-distribution",
                                            type="circle",
                                            children=[
                                                dcc.Graph(id='distribution-chart')
                                            ]
                                        )
                                    ], width=12, lg=8)
                                ])
                            ], className="p-3")
                        ]),
                    ], id="tabs", active_tab="tab-compare", className="custom-tabs mt-4")
                    
                ], width=12, lg=9)
            ])
            
        ], fluid=True, className="app-container pb-5")
        
    ], style={'minHeight': '100vh'})
