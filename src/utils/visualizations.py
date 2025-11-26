"""
Visualization Components
Advanced chart and map creators with production-ready styling
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from src.config import APP_CONFIG


class VisualizationFactory:
    """Factory for creating advanced visualizations"""
    
    def __init__(self, config=APP_CONFIG):
        self.config = config
        self.default_template = config.CHART_TEMPLATE
        self.color_schemes = config.COLOR_SCHEMES
    
    def create_choropleth_map(
        self, 
        df: pd.DataFrame, 
        metric: str,
        title: str,
        color_scheme: str = 'Blues',
        projection: str = 'natural earth'
    ) -> go.Figure:
        """
        Create beautiful choropleth map with custom styling
        
        Args:
            df: DataFrame with country data
            metric: Column name to visualize
            title: Chart title
            color_scheme: Plotly color scale
            projection: Map projection type
        """
        # Clean country names for ISO matching
        df_map = df.copy()
        
        # Create the choropleth
        fig = go.Figure(data=go.Choropleth(
            locations=df_map['Country'],
            z=df_map[metric],
            locationmode='country names',
            colorscale=color_scheme,
            autocolorscale=False,
            text=df_map['Country'],
            marker_line_color='white',
            marker_line_width=0.5,
            colorbar=dict(
                title=dict(
                    text=metric.replace('_', ' ').title(),
                    font=dict(size=14, family='Inter, sans-serif')
                ),
                thickness=15,
                len=0.7,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)',
                borderwidth=1,
                tickfont=dict(size=11)
            ),
            hovertemplate='<b>%{text}</b><br>' +
                         f'{metric.replace("_", " ").title()}: %{{z:,.2f}}<br>' +
                         '<extra></extra>'
        ))
        
        # Update layout with beautiful styling
        fig.update_geos(
            projection_type=projection,
            showcoastlines=True,
            coastlinecolor='rgba(0,0,0,0.3)',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            showcountries=True,
            countrycolor='white',
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showlakes=True,
            lakecolor='rgb(230, 245, 255)',
            bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=24, family='Outfit, Inter, sans-serif', color='#1a2332'),
                x=0.5,
                xanchor='center'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=700,
            margin=dict(l=0, r=0, t=80, b=0),
            font=dict(family='Inter, sans-serif'),
            hoverlabel=dict(
                bgcolor='white',
                font_size=13,
                font_family='Inter, sans-serif',
                bordercolor='#2196f3'
            )
        )
        
        return fig
    
    def create_3d_globe(
        self,
        df: pd.DataFrame,
        metric: str,
        title: str
    ) -> go.Figure:
        """Create interactive 3D globe visualization"""
        
        df_clean = df.dropna(subset=['Latitude', 'Longitude', metric])
        
        fig = go.Figure(data=go.Scattergeo(
            lon=df_clean['Longitude'],
            lat=df_clean['Latitude'],
            text=df_clean['Country'],
            mode='markers',
            marker=dict(
                size=df_clean[metric] / df_clean[metric].max() * 30 + 5,
                color=df_clean[metric],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title=metric.replace('_', ' ').title(),
                    thickness=15,
                    len=0.7
                ),
                line=dict(width=0.5, color='white'),
                opacity=0.8
            ),
            hovertemplate='<b>%{text}</b><br>' +
                         f'{metric.replace("_", " ").title()}: %{{marker.color:,.2f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_geos(
            projection_type='orthographic',
            showcoastlines=True,
            coastlinecolor='rgba(255,255,255,0.6)',
            showland=True,
            landcolor='rgb(40, 40, 40)',
            showcountries=True,
            countrycolor='rgba(255,255,255,0.3)',
            showocean=True,
            oceancolor='rgb(20, 20, 40)',
            bgcolor='rgb(10, 10, 20)'
        )
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=24, color='white'),
                x=0.5,
                xanchor='center'
            ),
            paper_bgcolor='rgb(10, 10, 20)',
            height=800,
            margin=dict(l=0, r=0, t=80, b=0),
            showlegend=False
        )
        
        return fig
    
    def create_comparison_radar(
        self,
        df: pd.DataFrame,
        countries: List[str],
        metrics: List[str]
    ) -> go.Figure:
        """Create radar chart for country comparison"""
        
        fig = go.Figure()
        
        colors = ['#2196f3', '#f44336', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4']
        
        for idx, country in enumerate(countries):
            country_data = df[df['Country'] == country]
            
            if country_data.empty:
                continue
            
            # Normalize values to 0-100 scale
            values = []
            for metric in metrics:
                val = country_data[metric].iloc[0]
                if pd.notna(val):
                    # Normalize based on global min-max
                    min_val = df[metric].min()
                    max_val = df[metric].max()
                    normalized = ((val - min_val) / (max_val - min_val)) * 100 if max_val != min_val else 50
                    values.append(normalized)
                else:
                    values.append(0)
            
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],  # Close the radar
                theta=[m.replace('_', ' ').title() for m in metrics] + [metrics[0].replace('_', ' ').title()],
                fill='toself',
                name=country,
                line=dict(color=colors[idx % len(colors)], width=2),
                fillcolor=colors[idx % len(colors)],
                opacity=0.3,
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             '%{theta}: %{r:.1f}/100<br>' +
                             '<extra></extra>'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=11),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, family='Inter, sans-serif')
                ),
                bgcolor='rgba(255,255,255,0.5)'
            ),
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5,
                font=dict(size=12)
            ),
            height=600,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif'),
            title=dict(
                text='Multi-Dimensional Country Comparison',
                font=dict(size=22, family='Outfit, Inter, sans-serif'),
                x=0.5,
                xanchor='center'
            )
        )
        
        return fig
    
    def create_scatter_correlation(
        self,
        df: pd.DataFrame,
        x_metric: str,
        y_metric: str,
        color_by: Optional[str] = None,
        size_by: Optional[str] = None
    ) -> go.Figure:
        """Create advanced scatter plot with correlation analysis"""
        
        df_clean = df.dropna(subset=[x_metric, y_metric])
        
        if color_by and color_by in df_clean.columns:
            color_data = df_clean[color_by]
        else:
            color_data = df_clean['Continent'] if 'Continent' in df_clean.columns else None
        
        if size_by and size_by in df_clean.columns:
            size_data = df_clean[size_by]
            # Normalize size
            size_data = (size_data - size_data.min()) / (size_data.max() - size_data.min()) * 50 + 10
        else:
            size_data = 15
        
        fig = px.scatter(
            df_clean,
            x=x_metric,
            y=y_metric,
            color=color_by if color_by else 'Continent',
            size=size_data if isinstance(size_data, pd.Series) else None,
            hover_name='Country',
            hover_data={x_metric: ':.2f', y_metric: ':.2f'},
            color_discrete_sequence=px.colors.qualitative.Set3,
            template=self.default_template
        )
        
        # Add trendline
        if len(df_clean) > 2:
            z = np.polyfit(df_clean[x_metric], df_clean[y_metric], 1)
            p = np.poly1d(z)
            x_trend = np.linspace(df_clean[x_metric].min(), df_clean[x_metric].max(), 100)
            
            fig.add_trace(go.Scatter(
                x=x_trend,
                y=p(x_trend),
                mode='lines',
                name='Trend',
                line=dict(color='red', width=2, dash='dash'),
                hovertemplate='Trendline<extra></extra>'
            ))
            
            # Calculate correlation
            correlation = df_clean[x_metric].corr(df_clean[y_metric])
            
            fig.add_annotation(
                text=f'Correlation: {correlation:.3f}',
                xref='paper',
                yref='paper',
                x=0.95,
                y=0.05,
                showarrow=False,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#2196f3',
                borderwidth=2,
                borderpad=10,
                font=dict(size=14, family='Inter, sans-serif')
            )
        
        fig.update_layout(
            title=dict(
                text=f'{y_metric.replace("_", " ").title()} vs {x_metric.replace("_", " ").title()}',
                font=dict(size=22, family='Outfit, Inter, sans-serif'),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title=x_metric.replace('_', ' ').title(),
            yaxis_title=y_metric.replace('_', ' ').title(),
            height=600,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='white',
            font=dict(family='Inter, sans-serif'),
            hovermode='closest'
        )
        
        fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        
        return fig
    
    def create_regional_bar_chart(
        self,
        df: pd.DataFrame,
        metric: str,
        aggregation: str = 'mean'
    ) -> go.Figure:
        """Create regional comparison bar chart"""
        
        if 'Continent' not in df.columns:
            return go.Figure()
        
        # Group by continent
        if aggregation == 'mean':
            regional_data = df.groupby('Continent')[metric].mean().sort_values(ascending=False)
        elif aggregation == 'sum':
            regional_data = df.groupby('Continent')[metric].sum().sort_values(ascending=False)
        elif aggregation == 'median':
            regional_data = df.groupby('Continent')[metric].median().sort_values(ascending=False)
        else:
            regional_data = df.groupby('Continent')[metric].mean().sort_values(ascending=False)
        
        colors = ['#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0', '#00bcd4', '#ffc107']
        
        fig = go.Figure(data=[
            go.Bar(
                x=regional_data.index,
                y=regional_data.values,
                marker=dict(
                    color=colors[:len(regional_data)],
                    line=dict(color='white', width=2)
                ),
                text=regional_data.values,
                texttemplate='%{text:.2f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>' +
                             f'{metric.replace("_", " ").title()}: %{{y:,.2f}}<br>' +
                             '<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=dict(
                text=f'{metric.replace("_", " ").title()} by Region ({aggregation.title()})',
                font=dict(size=22, family='Outfit, Inter, sans-serif'),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title='Region',
            yaxis_title=metric.replace('_', ' ').title(),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='white',
            font=dict(family='Inter, sans-serif'),
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        
        return fig
    
    def create_sunburst_chart(
        self,
        df: pd.DataFrame,
        metric: str
    ) -> go.Figure:
        """Create hierarchical sunburst chart"""
        
        df_clean = df.dropna(subset=['Continent', metric])
        
        # Create hierarchy: Continent -> Development Level -> Country
        if 'Development_Level' in df_clean.columns:
            fig = px.sunburst(
                df_clean,
                path=['Continent', 'Development_Level', 'Country'],
                values=metric,
                color=metric,
                color_continuous_scale='RdYlGn',
                template=self.default_template
            )
        else:
            fig = px.sunburst(
                df_clean,
                path=['Continent', 'Country'],
                values=metric,
                color=metric,
                color_continuous_scale='Viridis',
                template=self.default_template
            )
        
        fig.update_layout(
            title=dict(
                text=f'{metric.replace("_", " ").title()} Distribution',
                font=dict(size=22, family='Outfit, Inter, sans-serif'),
                x=0.5,
                xanchor='center'
            ),
            height=700,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif')
        )
        
        return fig
    
    def create_heatmap_correlation(
        self,
        df: pd.DataFrame,
        metrics: List[str]
    ) -> go.Figure:
        """Create correlation heatmap for multiple metrics"""
        
        # Calculate correlation matrix
        corr_matrix = df[metrics].corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=[m.replace('_', ' ').title() for m in corr_matrix.columns],
            y=[m.replace('_', ' ').title() for m in corr_matrix.index],
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont=dict(size=10),
            colorbar=dict(
                title='Correlation',
                thickness=15,
                len=0.7
            ),
            hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='Metrics Correlation Matrix',
                font=dict(size=22, family='Outfit, Inter, sans-serif'),
                x=0.5,
                xanchor='center'
            ),
            height=600,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif'),
            xaxis=dict(side='bottom'),
            yaxis=dict(side='left')
        )
        
        return fig
    
    def create_animated_timeline(
        self,
        df: pd.DataFrame,
        metric: str,
        time_column: str
    ) -> go.Figure:
        """Create animated timeline visualization (if time data available)"""
        
        # This is a placeholder for future time-series data
        # For now, create a static visualization
        
        return self.create_choropleth_map(df, metric, f'{metric.replace("_", " ").title()} Over Time')
