"""
Application Layout
Main layout structure for the Dash application
"""
from dash import html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dash_table


from src.components.ui_components import (
    create_navbar,
    create_stats_cards,
    create_filters_panel,
    create_comparison_panel,
    create_correlation_panel,
    create_distribution_panel,
    create_details_panel,
    create_overview_header,
    create_insights_panel,
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


    return html.Div(
        [
            # Theme + cross-view interaction state
            dcc.Store(id="ui-theme", data="light"),
            dcc.Store(id="selected-country", data=None),
            dcc.Store(id="selected-countries", data=[]),

            # Navbar
            create_navbar(),

            # Main container
            dbc.Container(
                [
                    # Header (quick context + actions)
                    html.Div(create_overview_header(), className="mt-4"),

                    # KPI cards
                    html.Div(create_stats_cards(merged_data), className="mt-3"),

                    dbc.Row(
                        [
                            # Left sidebar – filters always visible on lg+, scrollable
                            dbc.Col(
                                [
                                    create_filters_panel(metrics_info),
                                ],
                                width=12,
                                lg=3,
                                className="mb-4",
                            ),

                            # Main content
                            dbc.Col(
                                [
                                    dbc.Tabs(
                                        [
                                            dbc.Tab(
                                                label="✨ Overview",
                                                tab_id="tab-overview",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            html.Div(
                                                                                [
                                                                                    dcc.Loading(
                                                                                        id="loading-main-viz",
                                                                                        type="circle",
                                                                                        children=[
                                                                                            dcc.Graph(
                                                                                                id="main-visualization",
                                                                                                figure=default_fig,
                                                                                                config={
                                                                                                    "displayModeBar": True,
                                                                                                    "displaylogo": False,
                                                                                                },
                                                                                                style={"height": "560px"},
                                                                                            ),
                                                                                        ],
                                                                                    )
                                                                                ],
                                                                                className="viz-card viz-card--hero",
                                                                            ),
                                                                            html.Div(
                                                                                create_details_panel(),
                                                                                className="viz-card mt-3",
                                                                            ),
                                                                            html.Div(
                                                                                [
                                                                                    html.Div(
                                                                                        [
                                                                                            html.H5(
                                                                                                "Regional Summary",
                                                                                                className="panel-title",
                                                                                            ),
                                                                                            html.Div(
                                                                                                "Aggregated view by continent.",
                                                                                                className="panel-subtitle",
                                                                                            ),
                                                                                        ],
                                                                                        className="panel-header",
                                                                                    ),
                                                                                    dcc.Loading(
                                                                                        id="loading-overview-regional",
                                                                                        type="circle",
                                                                                        children=[
                                                                                            dcc.Graph(
                                                                                                id="overview-regional",
                                                                                                config={
                                                                                                    "displayModeBar": True,
                                                                                                    "displaylogo": False,
                                                                                                    "toImageButtonOptions": {
                                                                                                        "format": "png",
                                                                                                        "filename": "regional_overview",
                                                                                                        "height": 1920,
                                                                                                        "width": 2560,
                                                                                                        "scale": 4
                                                                                                    },
                                                                                                    "modeBarButtonsToAdd": ["toImage"]
                                                                                                },
                                                                                                style={"height": "320px"},
                                                                                            )
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                                className="viz-card mt-3",
                                                                            ),
                                                                        ],
                                                                        width=12,
                                                                        lg=8,
                                                                        className="mb-4",
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            html.Div(
                                                                                [
                                                                                    html.Div(
                                                                                        [
                                                                                            html.H5(
                                                                                                "Top / Bottom Ranking",
                                                                                                className="panel-title",
                                                                                            ),
                                                                                            html.Div(
                                                                                                "Auto-updates with filters and selected metric.",
                                                                                                className="panel-subtitle",
                                                                                            ),
                                                                                        ],
                                                                                        className="panel-header",
                                                                                    ),
                                                                                    dcc.Loading(
                                                                                        id="loading-rank",
                                                                                        type="circle",
                                                                                        children=[
                                                                                            dcc.Graph(
                                                                                                id="rank-chart",
                                                                                                config={
                                                                                                    "displayModeBar": True,
                                                                                                    "displaylogo": False,
                                                                                                    "toImageButtonOptions": {
                                                                                                        "format": "png",
                                                                                                        "filename": "ranking_chart",
                                                                                                        "height": 1800,
                                                                                                        "width": 2400,
                                                                                                        "scale": 4
                                                                                                    },
                                                                                                    "modeBarButtonsToAdd": ["toImage"]
                                                                                                },
                                                                                                style={"height": "300px"},
                                                                                            )
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                                className="viz-card",
                                                                            ),
                                                                            html.Div(
                                                                                [
                                                                                    html.Div(
                                                                                        [
                                                                                            html.H5(
                                                                                                "Relationship Explorer",
                                                                                                className="panel-title",
                                                                                            ),
                                                                                            html.Div(
                                                                                                "Context-aware comparison (auto-picks a relevant reference metric).",
                                                                                                className="panel-subtitle",
                                                                                            ),
                                                                                        ],
                                                                                        className="panel-header",
                                                                                    ),
                                                                                    dcc.Loading(
                                                                                        id="loading-overview-scatter",
                                                                                        type="circle",
                                                                                        children=[
                                                                                            dcc.Graph(
                                                                                                id="overview-scatter",
                                                                                                config={
                                                                                                    "displayModeBar": True,
                                                                                                    "displaylogo": False,
                                                                                                    "toImageButtonOptions": {
                                                                                                        "format": "png",
                                                                                                        "filename": "relationship_explorer",
                                                                                                        "height": 1800,
                                                                                                        "width": 2400,
                                                                                                        "scale": 4
                                                                                                    },
                                                                                                    "modeBarButtonsToAdd": ["toImage"]
                                                                                                },
                                                                                                style={"height": "300px"},
                                                                                            )
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                                className="viz-card mt-3",
                                                                            ),
                                                                            html.Div(
                                                                                [
                                                                                    html.Div(
                                                                                        [
                                                                                            html.H5(
                                                                                                "Spread Snapshot",
                                                                                                className="panel-title",
                                                                                            ),
                                                                                            html.Div(
                                                                                                "How the metric varies across continents (box plot).",
                                                                                                className="panel-subtitle",
                                                                                            ),
                                                                                        ],
                                                                                        className="panel-header",
                                                                                    ),
                                                                                    dcc.Loading(
                                                                                        id="loading-overview-spread",
                                                                                        type="circle",
                                                                                        children=[
                                                                                            dcc.Graph(
                                                                                                id="overview-spread",
                                                                                                config={
                                                                                                    "displayModeBar": True,
                                                                                                    "displaylogo": False,
                                                                                                    "toImageButtonOptions": {
                                                                                                        "format": "png",
                                                                                                        "filename": "spread_snapshot",
                                                                                                        "height": 1560,
                                                                                                        "width": 2080,
                                                                                                        "scale": 4
                                                                                                    },
                                                                                                    "modeBarButtonsToAdd": ["toImage"]
                                                                                                },
                                                                                                style={"height": "260px"},
                                                                                            )
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                                className="viz-card mt-3",
                                                                            ),
                                                                            html.Div(
                                                                                create_insights_panel(),
                                                                                className="viz-card mt-3",
                                                                            ),
                                                                        ],
                                                                        width=12,
                                                                        lg=4,
                                                                        className="mb-4",
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        className="p-3",
                                                    )
                                                ],
                                            ),
                                            dbc.Tab(
                                                label="🔍 Compare",
                                                tab_id="tab-compare",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [create_comparison_panel(country_list)],
                                                                        width=12,
                                                                        lg=4,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dcc.Loading(
                                                                                id="loading-comparison",
                                                                                type="circle",
                                                                                children=[dcc.Graph(
                                                                                    id="comparison-chart",
                                                                                    config={
                                                                                        "displayModeBar": True,
                                                                                        "displaylogo": False,
                                                                                        "toImageButtonOptions": {
                                                                                            "format": "png",
                                                                                            "filename": "comparison_chart",
                                                                                            "height": 2400,
                                                                                            "width": 3200,
                                                                                            "scale": 4
                                                                                        },
                                                                                        "modeBarButtonsToAdd": ["toImage"]
                                                                                    }
                                                                                )],
                                                                            )
                                                                        ],
                                                                        width=12,
                                                                        lg=8,
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        className="p-3",
                                                    )
                                                ],
                                            ),
                                            dbc.Tab(
                                                label="📈 Correlation",
                                                tab_id="tab-correlation",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [create_correlation_panel()],
                                                                        width=12,
                                                                        lg=4,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dcc.Loading(
                                                                                id="loading-correlation",
                                                                                type="circle",
                                                                                children=[
                                                                                    html.Div(
                                                                                        [
                                                                                            dcc.Graph(
                                                                                                id="correlation-chart",
                                                                                                config={
                                                                                                    "displayModeBar": True,
                                                                                                    "displaylogo": False,
                                                                                                    "toImageButtonOptions": {
                                                                                                        "format": "png",
                                                                                                        "filename": "correlation_scatter",
                                                                                                        "height": 2640,
                                                                                                        "width": 2640,
                                                                                                        "scale": 4
                                                                                                    },
                                                                                                    "modeBarButtonsToAdd": ["toImage"]
                                                                                                },
                                                                                                style={
                                                                                                    "width": "50%",
                                                                                                    "display": "inline-block",
                                                                                                    "verticalAlign": "top",
                                                                                                    "height": "440px",
                                                                                                },
                                                                                            ),
                                                                                            dcc.Graph(
                                                                                                id="heatmap-chart",
                                                                                                config={
                                                                                                    "displayModeBar": True,
                                                                                                    "displaylogo": False,
                                                                                                    "toImageButtonOptions": {
                                                                                                        "format": "png",
                                                                                                        "filename": "correlation_heatmap",
                                                                                                        "height": 2640,
                                                                                                        "width": 2640,
                                                                                                        "scale": 4
                                                                                                    },
                                                                                                    "modeBarButtonsToAdd": ["toImage"]
                                                                                                },
                                                                                                style={
                                                                                                    "width": "50%",
                                                                                                    "display": "inline-block",
                                                                                                    "verticalAlign": "top",
                                                                                                    "height": "440px",
                                                                                                },
                                                                                            ),
                                                                                        ]
                                                                                    )
                                                                                ],
                                                                            )
                                                                        ],
                                                                        width=12,
                                                                        lg=8,
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        className="p-3",
                                                    )
                                                ],
                                            ),
                                            dbc.Tab(
                                                label="🌍 Regional",
                                                tab_id="tab-regional",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dcc.Loading(
                                                                id="loading-regional",
                                                                type="circle",
                                                                children=[dcc.Graph(
                                                                    id="regional-chart",
                                                                    config={
                                                                        "displayModeBar": True,
                                                                        "displaylogo": False,
                                                                        "toImageButtonOptions": {
                                                                            "format": "png",
                                                                            "filename": "regional_analysis",
                                                                            "height": 2400,
                                                                            "width": 3200,
                                                                            "scale": 4
                                                                        },
                                                                        "modeBarButtonsToAdd": ["toImage"]
                                                                    }
                                                                )],
                                                            )
                                                        ],
                                                        className="p-3",
                                                    )
                                                ],
                                            ),
                                            dbc.Tab(
                                                label="📊 Distribution",
                                                tab_id="tab-distribution",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [create_distribution_panel(metrics_info)],
                                                                        width=12,
                                                                        lg=4,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dcc.Loading(
                                                                                id="loading-distribution",
                                                                                type="circle",
                                                                                children=[dcc.Graph(
                                                                                    id="distribution-chart",
                                                                                    config={
                                                                                        "displayModeBar": True,
                                                                                        "displaylogo": False,
                                                                                        "toImageButtonOptions": {
                                                                                            "format": "png",
                                                                                            "filename": "distribution_analysis",
                                                                                            "height": 2400,
                                                                                            "width": 3200,
                                                                                            "scale": 4
                                                                                        },
                                                                                        "modeBarButtonsToAdd": ["toImage"]
                                                                                    }
                                                                                )],
                                                                            )
                                                                        ],
                                                                        width=12,
                                                                        lg=8,
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        className="p-3",
                                                    )
                                                ],
                                            ),
                                            dbc.Tab(
                                                label="🧾 Data",
                                                tab_id="tab-data",
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.H5("Filtered Dataset", className="panel-title"),
                                                                    html.Div(
                                                                        "Exports can be added next (CSV/Excel/JSON).",
                                                                        className="panel-subtitle",
                                                                    ),
                                                                ],
                                                                className="panel-header",
                                                            ),
                                                            dash_table.DataTable(
                                                                id="data-table",
                                                                columns=[],
                                                                data=[],
                                                                page_size=12,
                                                                sort_action="native",
                                                                filter_action="native",
                                                                style_table={"overflowX": "auto"},
                                                                style_header={
                                                                    "backgroundColor": "rgba(255,255,255,0.9)",
                                                                    "fontWeight": "700",
                                                                    "border": "none",
                                                                },
                                                                style_cell={
                                                                    "padding": "10px",
                                                                    "border": "none",
                                                                    "fontFamily": "Inter, sans-serif",
                                                                    "fontSize": "13px",
                                                                },
                                                                style_data_conditional=[
                                                                    {
                                                                        "if": {"row_index": "odd"},
                                                                        "backgroundColor": "rgba(0,0,0,0.02)",
                                                                    }
                                                                ],
                                                            ),
                                                        ],
                                                        className="p-3 viz-card",
                                                    )
                                                ],
                                            ),
                                        ],
                                        id="tabs",
                                        active_tab="tab-overview",
                                        className="custom-tabs",
                                    )
                                ],
                                width=12,
                                lg=9,
                            ),
                        ]
                    ),
                ],
                fluid=True,
                className="app-container pb-5",
            ),
        ],
        id="app-root",
        className="theme-light",
        style={"minHeight": "100vh"},
    )
