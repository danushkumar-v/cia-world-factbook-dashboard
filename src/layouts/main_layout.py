"""
Application Layout
Main layout structure for the Dash application
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.components.ui_components import (
    create_navbar,
    create_stats_cards,
    create_filters_panel,
    create_comparison_panel,
    create_correlation_panel
)


def create_layout(merged_data, metrics_info, country_list):
    """Create the main application layout"""
    
    # Update continent filter options
    continents = sorted(merged_data['Continent'].unique())
    continents = [c for c in continents if c != 'Other']
    
    # Update development level filter options
    dev_levels = merged_data['Development_Level'].dropna().unique()
    
    return html.Div([
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
                                    id='main-visualization',
                                    config={'displayModeBar': True, 'displaylogo': False},
                                    style={'height': '700px'}
                                )
                            ]
                        )
                    ], className="chart-container mb-4"),
                    
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
                                                dcc.Graph(id='correlation-chart')
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
                    ], id="tabs", active_tab="tab-compare", className="custom-tabs mt-4")
                    
                ], width=12, lg=9)
            ])
            
        ], fluid=True, className="app-container pb-5")
        
    ], style={'minHeight': '100vh'})
