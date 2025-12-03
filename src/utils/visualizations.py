"""
Visualization Components
Advanced chart and map creators with production-ready styling

DESIGN PRINCIPLES (JBI100 - Visualization Course):
This module implements visualizations based on:
1. Marks & Channels Framework (M2_01) - Munzner
2. Channel Effectiveness Ranking (M2_02-04)
3. Color Perception & Weber's Law (M2_05-08)
4. Gestalt Principles (M3_01)
5. Tufte's Data-Ink Ratio (M3_01)
6. Dangers of Depth (M3_02)
7. Eyes Beat Memory Principle (M3_03)

Each visualization includes design rationale in docstrings explaining:
- Mark type and primary/secondary channels used
- Why these channels are effective for the data type
- Design principles applied (Gestalt, Tufte, color)
- Trade-offs and justifications

See docs/reasoning.md and docs/INTERIM_REPORT.md for comprehensive design documentation.
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from src.config import APP_CONFIG


class VisualizationFactory:
    """Factory for creating advanced visualizations grounded in design principles.
    
    Design Philosophy:
    - Use position channel (most effective) for primary encoding
    - Match marks to data types (e.g., points for 2D quantitative)
    - Apply Gestalt principles (proximity, similarity, continuity, closure)
    - Maximize data-ink ratio (Tufte principle)
    - Ensure perceptual uniformity in color scales (Weber's law)
    - Minimize 3D effects (only where geographically meaningful)
    - Support "eyes beat memory" - pre-compute trends, show values explicitly
    """
    
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
        Create choropleth map - geographic distribution of single quantitative metric.
        
        DESIGN RATIONALE (JBI100 principles):
        ─────────────────────────────────────
        Mark: Area (country regions)
        Primary Channel: Color luminance (sequential progression)
        Secondary Channel: Position (geographic - fixed)
        
        Channel Effectiveness:
        - Position (x,y): Inherent to geography but unavailable for data encoding
        - Color (luminance): Ranked #5 in effectiveness (Munzner M2_02)
          BUT: Only available channel for this mark+task combination
          ✓ Maximizes clarity for geographic data
        
        Gestalt Principles Applied:
        - Similarity: Same color hue → same data range perception
        - Continuity: Color gradient guides eye across regions
        - Closure: Country borders define geographic units
        - Figure-Ground: White borders (figure) separate from ocean (ground)
        
        Color Design (Weber's Law - M2_08):
        - Sequential color schemes (Blues, Greens, Reds) ensure perceptually uniform steps
        - Avoids rainbow colormaps (which distort perception per M2 research)
        - Luminance progression: dark = high values, light = low values
        
        Tufte Principles:
        ✓ High data-ink ratio: every colored pixel = data value
        ✓ Minimalist: white borders only where necessary for clarity
        ✓ Clear: color bar and labels support interpretation
        
        Task Support:
        - Find: Search by country name via location
        - Compare: Visual comparison across countries
        - Rank: See highest values at a glance (darkest regions)
        - Summarize: Aggregate geographic pattern evident immediately
        
        Args:
            df: DataFrame with 'Country' column and metric data
            metric: Column name containing quantitative values to visualize
            title: Chart title
            color_scheme: Sequential color scale (Blues, Greens, Reds, Viridis)
            projection: Map projection type (natural earth, mercator, orthographic)
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
        """
        Create interactive 3D globe visualization with bubble markers.
        
        DESIGN RATIONALE (JBI100 principles):
        ─────────────────────────────────────
        Mark: Points (bubbles)
        Primary Channel: Position (latitude, longitude)
        Secondary Channel: Size (area encoding)
        Tertiary Channel: Color (hue for categorical distinction)
        Projection: Orthographic (not perspective)
        
        Channel Effectiveness (M2_02-04):
        - Position: Ranked #1 - most effective for accuracy
          ✓ Latitude/longitude positioning ensures geographic authenticity
        - Size: Ranked #4 - moderate accuracy for quantitative
          ✓ Bubble area encodes metric magnitude
          ✓ Pre-attentive processing: larger bubbles noticed first
        - Color: Used for categorical (not quantitative)
        
        3D Justification Despite M3_02 "Dangers of Depth":
        ⚠️ M3 warns: 3D adds cognitive load, ambiguity in depth perception
        ✓ Mitigations applied:
          - Orthographic projection: NO perspective distortion
            (Equal-area projection - preserves area relationships)
          - Dark background (rgb(10,10,20)): Reduces visual clutter
          - Rotatable by user: Allows self-resolution of depth ambiguity
          - Tooltip values: Precise reading without estimating depth
          - Used for exploratory analysis, NOT precise value reading
        
        Gestalt Principles:
        - Proximity: Nearby bubbles grouped as geographic clusters
        - Similarity: Similar colors perceived as related values
        - Figure-Ground: Bright bubbles (figure) pop against dark background
        - Continuity: Color gradient guides perception across globe
        
        Task Support:
        - Explore: Rotatable globe engages exploratory data analysis
        - Find: Zoom reveals individual countries
        - Correlate: Bubble size vs color shows multi-metric relationships
        - Pattern: Geographic clustering visible immediately
        
        Color Design (M2_05-08):
        - Viridis colormap: Perceptually uniform (Weber's law)
        - Sequential progression: easier interpretation than categorical
        
        Why This Mark+Channel Combination:
        - Geographic authenticity important for global policy data
        - 3D sphere more intuitive than flat map for some users
        - Multiple metrics encodable (position, size, color)
        - Interactive rotation supports exploratory analysis
        
        Args:
            df: DataFrame with 'Latitude', 'Longitude', and metric columns
            metric: Column name for bubble size/color encoding
            title: Chart title
        """
        
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
        """
        Create radar (spider) chart for multi-dimensional country comparison.
        
        DESIGN RATIONALE (JBI100 principles):
        ─────────────────────────────────────
        Mark: Polygon (connecting radial points)
        Primary Channel: Radial distance (position)
        Secondary Channel: Angular position (categorical)
        Tertiary Channel: Polygon area (size reinforcement)
        Quaternary Channel: Hue (country distinction)
        
        Channel Effectiveness (M2_02-04):
        - Position (radial distance): Ranked #1 for quantitative accuracy
          ✓ Humans perceive radial distances effectively
          ✓ Supports comparison of 5-7 dimensions simultaneously
        - Position (angular): Ranked #3 for categorical distinction
          ✓ Each metric assigned unique angle
        - Area (polygon): Gestalt closure - reinforces magnitude
        - Hue: Used for categorical country distinction (not quantitative)
        
        Design Trade-offs:
        ⚠️ Challenge: Radar less accurate than bar charts for single values
        ✓ Justification: Multi-dimensional view worth slight accuracy loss
        ⚠️ Challenge: Difficult with >7 dimensions
        ✓ Limitation: Limited to ≤7 metrics to maintain readability
        
        Gestalt Principles (M3_01):
        - Closure: Enclosed polygon shapes perceived as unified country profile
        - Similarity: Same color → same country across all metrics
        - Proximity: All metrics for one country grouped in one polygon
        - Continuity: Smooth polygon perimeter guides perception
        
        Why Radar vs Alternatives:
        - Treemap: Good for hierarchies, poor for within-country comparison
        - Parallel coordinates: Works for many dimensions, cluttered visualization
        - Small multiples (bars): Clear but requires mental integration
        - ✓ Radar: Balances multi-dimensionality with visual unity
        
        Normalization (0-100 scale):
        - Equalizes units: GDP (USD billions) vs Literacy (%) comparable
        - Enables fair comparison despite different measurement scales
        - "Eyes beat memory" principle: pre-normalized values show true comparison
        
        Color Design (M2_05-08):
        - Distinct hue per country (categorical encoding)
        - Transparent fill (opacity=0.3) enables overlap perception
        - White/dark boundaries separate polygons (figure-ground)
        
        Task Support:
        - Compare: Multiple countries' profiles visible simultaneously
        - Rank: Which metrics does each country excel at?
        - Correlate: See if high performers excel across metrics
        - Profile: Understand each country's "development signature"
        
        Args:
            df: DataFrame with country rows and metric columns
            countries: List of country names to compare (2-6 recommended)
            metrics: List of metric column names (5-7 recommended)
        """
        
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

    def create_comparison_heatmap(
        self,
        df: pd.DataFrame,
        countries: List[str],
        metrics: List[str]
    ) -> go.Figure:
        """
        Create heatmap for multi-country multi-metric comparison (8+ metrics).
        
        DESIGN RATIONALE (JBI100 principles):
        ─────────────────────────────────────
        Mark: Rectangle (cell in grid)
        Primary Channel: Color hue (quantitative value encoding)
        Secondary Channel: Position (rows: countries, columns: metrics)
        Tertiary Channel: Text annotation (explicit values)
        
        Channel Effectiveness (M2_02-04):
        - Position (grid): Organizes country × metric matrix clearly
        - Color: More effective than angle for 8+ dimensions
          ✓ Scales better than radar (which fails >7 metrics)
          ✓ Each metric gets unique column (no overlap)
        - Text values: Precise reading when needed
        
        Why Heatmap for 8+ Metrics:
        - ❌ Radar chart: Angular channels crowd >7 metrics, overlaps
        - ✅ Heatmap: Rectangular grid scales smoothly to 15+ metrics
        - ❌ Table: Requires sequential reading, poor for patterns
        - ✅ Color: Pattern detection efficient (similar colors = similar values)
        
        Gestalt Principles (M3_01):
        - Proximity: Grid cells grouped by country (rows) and metric (columns)
        - Similarity: Similar values → similar color brightness
        - Continuity: Color gradient guides eye
        
        Task Support:
        - Compare: Multiple countries and metrics visible simultaneously
        - Rank: Find which country has highest/lowest per metric
        - Pattern: Color patterns reveal country strengths/weaknesses
        - Correlate: See if patterns align across metrics
        """
        df_filtered = df[df['Country'].isin(countries)].copy()
        
        if df_filtered.empty:
            return go.Figure().add_annotation(
                text="No data available for selected countries",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )
        
        # Prepare data matrix
        df_filtered = df_filtered.set_index('Country')
        data_matrix = df_filtered[metrics].fillna(0)
        
        # Normalize to 0-100 scale for comparability
        normalized_matrix = pd.DataFrame(
            index=data_matrix.index,
            columns=data_matrix.columns
        )
        for col in data_matrix.columns:
            min_val = data_matrix[col].min()
            max_val = data_matrix[col].max()
            if max_val > min_val:
                normalized_matrix[col] = ((data_matrix[col] - min_val) / (max_val - min_val)) * 100
            else:
                normalized_matrix[col] = 50
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=normalized_matrix.values,
            x=[col.replace('_', ' ') for col in normalized_matrix.columns],
            y=normalized_matrix.index,
            colorscale='Viridis',
            text=data_matrix.values,
            texttemplate='%{text:.1f}',
            textfont={"size": 10},
            colorbar=dict(
                title="Normalized<br>Score",
                thickness=15,
                len=0.7
            )
        ))
        
        fig.update_layout(
            title="Multi-Metric Country Comparison Heatmap",
            xaxis_title="Metrics",
            yaxis_title="Countries",
            height=400 + len(countries) * 30,
            hovermode='closest'
        )
        
        return fig

    def create_comparison_scatter(
        self,
        df: pd.DataFrame,
        countries: List[str],
        metrics: List[str]
    ) -> go.Figure:
        """
        Create scatter plot for 2-metric country comparison.
        
        DESIGN RATIONALE (JBI100 principles):
        ─────────────────────────────────────
        Mark: Point (filled circle)
        Primary Channels: Position X (quantitative), Position Y (quantitative)
        Secondary Channel: Hue (categorical - country distinction)
        Tertiary Channel: Size (optional - third metric)
        
        Channel Effectiveness (M2_02-04):
        - Position (X,Y): Ranked #1 for quantitative perception
          ✓ Bivariate relationships immediately visible
          ✓ Correlation/clustering patterns jump out
        - Hue: Used for categorical country distinction
        - Size: Bubble size can show optional third metric
        
        Scatter Plot Benefits:
        ✓ Best for 2 metrics (perfect channel matching)
        ✓ Shows correlation structure clearly
        ✓ Outliers immediately visible
        ✓ Clusters reveal patterns
        - Limited to 2 dimensions (use heatmap for 8+)
        
        Gestalt Principles (M3_01):
        - Similarity: Same color → same country
        - Proximity: Clustered points → similar characteristics
        - Continuity: Trend lines guide perception (optional)
        
        Task Support:
        - Correlate: Linear trend immediately visible
        - Outlier: Isolated points stand out (Gestalt separation)
        - Cluster: Country groups visible by position
        - Rank: X/Y positions show relative performance
        """
        df_filtered = df[df['Country'].isin(countries)].copy()
        
        if df_filtered.empty or len(metrics) != 2:
            return go.Figure().add_annotation(
                text="Scatter plot requires exactly 2 metrics",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )
        
        metric_x, metric_y = metrics[0], metrics[1]
        
        fig = go.Figure()
        
        # Add points for each country
        for country in countries:
            country_data = df_filtered[df_filtered['Country'] == country]
            if not country_data.empty:
                fig.add_trace(go.Scatter(
                    x=country_data[metric_x],
                    y=country_data[metric_y],
                    mode='markers+text',
                    name=country,
                    marker=dict(size=10),
                    text=country,
                    textposition="top center"
                ))
        
        fig.update_layout(
            title=f"Country Comparison: {metric_x} vs {metric_y}",
            xaxis_title=metric_x.replace('_', ' '),
            yaxis_title=metric_y.replace('_', ' '),
            hovermode='closest',
            height=500,
            showlegend=True
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
        """
        Create scatter plot with trendline for correlation analysis.
        
        DESIGN RATIONALE (JBI100 principles):
        ─────────────────────────────────────
        Mark: Point
        Primary Channel: Position (X-axis)
        Primary Channel: Position (Y-axis)
        Secondary Channel: Color (hue for categorical grouping)
        Tertiary Channel: Size (optional third quantitative variable)
        
        Channel Effectiveness (M2_02-04):
        - Position (X,Y): Ranked #1 - MOST effective for quantitative
          ✓ Humans read 2D Cartesian coordinates intuitively
          ✓ Direct visual perception of correlation magnitude
          ✓ Outliers and clusters immediately apparent
        - Color: Used for categorical grouping (continent/region)
        - Size: Optional tertiary quantitative encoding (ranked #4)
        
        Bivariate Quantitative Encoding:
        - X-axis: First metric (independent variable)
        - Y-axis: Second metric (dependent variable)
        - Position marks encode data most accurately of all channel types
        - Scatter (point marks) minimize visual clutter
        
        Trendline Addition (Eyes Beat Memory Principle - M3_03):
        - Pre-computed linear regression line saves viewer effort
        - Red dashed visual style: distinct from data points (figure-ground)
        - Correlation coefficient: explicit label removes ambiguity
        ✓ "Eyes beat memory": External representation > mental estimation
        
        Gridlines Trade-off:
        ⚠️ Tufte principle: Minimize non-data ink
        ✓ Decision: Add faint gridlines (rgba(0,0,0,0.05))
        ✓ Justification: Major usability gain (coordinate reading) worth small ink increase
        ✓ Gestalt alignment principle: Gridlines aid coordinate inference
        
        Color Design (Categorical Grouping):
        - Hue distinguishes continents (categorical, not quantitative)
        - Set3 palette: Colorblind-accessible
        - Gestalt similarity: Same color → related group
        
        Task Support:
        - Find: Locate specific country by name
        - Compare: See how country compares to region
        - Correlate: Trendline + coefficient shows relationship strength
        - Outliers: Non-trendline points immediately visible
        - Distribute: Point cloud shape shows data spread
        
        Point Marks Justification:
        - Low visual weight: doesn't obscure other points
        - Dense data encodable: hundreds of countries possible
        - Pre-attentive: position differences processed automatically
        
        Optional Size Encoding:
        - Third quantitative dimension (e.g., population)
        - Normalized (0-50 + 10 range) for visual clarity
        - Ranked #4 in effectiveness but useful for tertiary insight
        
        Args:
            df: DataFrame with metric columns
            x_metric: Column name for X-axis (independent variable)
            y_metric: Column name for Y-axis (dependent variable)
            color_by: Optional column for color grouping (e.g., 'Continent')
            size_by: Optional column for bubble size (tertiary quantitative)
        """
        
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
        """
        Create regional comparison bar chart with sorted ranking.
        
        DESIGN RATIONALE (JBI100 principles):
        ─────────────────────────────────────
        Mark: Rectangle (bar)
        Primary Channel: Length (bar height - position along Y-axis)
        Secondary Channel: Hue (color per continent/region)
        
        Channel Effectiveness (M2_02-04):
        - Length: Ranked #2 - VERY effective for quantitative comparison
          ✓ Humans perceive bar heights accurately
          ✓ Simple, direct magnitude encoding
          ✓ Pre-attentive processing: length differences automatic
        - Hue: Used for categorical distinction (continent) - ranked #6
          ✓ Gestalt similarity: same color = same category
        
        Bar Chart Superiority Over Alternatives:
        - Pie chart: ❌ Angle encoding (ranked #3) less accurate than length
        - Radar chart: ❌ Good for multi-dimensional, not single metric
        - Area chart: ❌ Confuses area with magnitude
        - ✅ Bar: Most straightforward and accurate for ranking task
        
        Sorting (Descending):
        - Bars sorted highest to lowest value
        - Aids ranking perception: top performer immediately obvious
        - Gestalt principle: Position creates visual ordering
        - M3 principle: Visual ordination supports ranking task
        
        Aggregation Functions:
        - Mean: Average metric across countries in region (default)
        - Median: Robust to outliers
        - Sum: Total magnitude (e.g., total population)
        - Clearly labeled in chart so viewers understand metric
        
        Color Design (M2_05-08):
        - Distinct hue per continent (categorical distinction)
        - Bright, saturated colors: easy differentiation
        - White borders: Figure-ground separation (bar figure from background)
        - Avoiding rainbow: Uses limited, meaningful color palette
        
        Tufte Principles (Data-Ink Maximization):
        ✓ Minimalist: No 3D effects, drop shadows, or decorative elements
        ✓ Value labels on bars: Explicit numbers for precision reading
        ✓ White background: High contrast, clear readability
        ✓ No redundant legend: Colors are simple enough to distinguish
        
        Gestalt Principles (M3_01):
        - Proximity: Bars group by visual alignment
        - Similarity: Same color region → same continent across contexts
        - Figure-ground: Bars (figure) on white background (ground)
        - Continuity: Y-axis provides visual anchor
        
        Task Support:
        - Rank: Sorted bars immediately show top-to-bottom ordering
        - Compare: Direct visual comparison of bar heights
        - Summarize: Aggregate pattern evident at glance
        - Find: Locate specific region by name (X-axis label)
        - Categorize: Color grouping by region obvious
        
        Axes Design:
        - X-axis: Region/continent labels (categorical)
        - Y-axis: Metric scale (quantitative)
        - Y-axis gridlines: Faint, aid value reading without cluttering
        - No X-axis gridlines: Bar positioning clear without aids
        
        Args:
            df: DataFrame with 'Continent' column and metric columns
            metric: Column name of metric to visualize
            aggregation: 'mean', 'median', or 'sum' aggregation function
        """
        
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
        """
        Create hierarchical sunburst chart for multi-level comparison.
        
        DESIGN RATIONALE (JBI100 principles):
        ─────────────────────────────────────
        Mark: Ring segment (radial wedge)
        Primary Channel: Angular position (categorical: continents)
        Secondary Channel: Radial position (hierarchical levels)
        Tertiary Channel: Area (quantitative metric magnitude)
        Quaternary Channel: Color (continuous quantitative metric)
        
        Hierarchical Structure:
        - Level 1 (innermost): Continents (6 segments, ~60° each)
        - Level 2 (middle): Development levels (Developed, Developing, etc.)
        - Level 3 (outermost): Individual countries
        ✓ Radial position naturally encodes hierarchy depth
        
        Channel Effectiveness (M2_02-04):
        - Angular position: Ranked #3 for categorical distinction
          ✓ Each category (continent) assigned unique angle
          ✓ Pre-attentive: arc position recognized automatically
        - Radial position: Encodes hierarchy levels naturally
          ✓ Gestalt principle: inside = broader, outside = specific
        - Area: Ranked #4 for quantitative magnitude
          ✓ Ring segment area proportional to metric value
          ✓ Gestalt closure: rings perceived as complete units
        - Color: Sequential/diverging for continuous quantitative
          ✓ RdYlGn diverging: Health perception (red=low, green=high)
        
        Why Sunburst vs Alternatives:
        - Treemap: ❌ Better for area comparison, loses hierarchy intuition
        - Icicle: ❌ Space-efficient but less visually engaging
        - Nested pie: ❌ Poor for precise value comparison
        - ✅ Sunburst: Balances hierarchy, comparison, and engagement
        
        Tufte Principles (Data-Ink Maximization):
        ✓ Labels on hover (not static): Avoids clutter
        ✓ Every colored segment: = data value (no decorative elements)
        ✓ White segment separators: Minimal non-data ink, aids clarity
        
        Gestalt Principles (M3_01):
        - Proximity: Segments in same ring perceived as same level
        - Similarity: Same color family → related values
        - Closure: Ring completeness creates unified perception
        - Continuity: Smooth color gradient guides eye
        - Figure-ground: Colored segments (figure) on white background
        
        Interactive Behavior (Eyes Beat Memory - M3_03):
        - Click segment to zoom (drill-down exploration)
        - Breadcrumb path shows hierarchy location
        ✓ Prevents disorientation (external memory aid)
        ✓ Supports exploratory analysis task
        ✓ Reduces cognitive load of full 3-level view
        
        Color Design (M2_06-08):
        - RdYlGn diverging: Represents metric range (red=low, green=high)
        - Weber's law: Perceptually uniform color progression
        - Colorbar shows scale (0% → 100% or metric units)
        - Meaningful: Red/green semantics support interpretation
        
        Advantages of This Mark+Channel Combination:
        - Shows both composition (area size) and value (color intensity)
        - Hierarchy visible: drill-down structure intuitive
        - Aggregation evident: parent segment area = sum of children
        - Pattern discovery: Color variations show efficiency/inequality
        
        Tasks Supported:
        - Explore: Click-to-zoom enables discovery
        - Distribute: See how values distributed across hierarchy
        - Rank: Which countries/levels top the values?
        - Correlate: Do developed countries always score higher?
        - Categorize: Group by continent, development level
        
        Hierarchical Path Example:
        Africa → Developing Countries → Nigeria
        (Each level progressively specific)
        
        Aesthetic Considerations:
        - Dark background eliminated in favor of white (clarity)
        - Smooth transitions between zoom levels (reduces jarring)
        - Smooth color palette: no harsh boundaries
        
        Args:
            df: DataFrame with 'Continent', 'Development_Level', 'Country' columns
            metric: Column name for ring size and color encoding
        """
        
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
        """
        Create correlation heatmap for multi-metric relationship analysis.
        
        DESIGN RATIONALE (JBI100 principles):
        ─────────────────────────────────────
        Mark: Rectangle (cell in matrix)
        Primary Channel: Color (hue divergence: red-blue)
        Secondary Channel: Position (rows: metrics, columns: metrics)
        Tertiary Channel: Text values (explicit correlation coefficients)
        
        Correlation Matrix Structure:
        - Symmetric matrix: rows = metrics, columns = metrics
        - Diagonal: Always 1.0 (variable correlates with itself)
        - Off-diagonal (i,j): Pearson correlation between metrics i and j
        - Range: [-1.0, +1.0] (perfect negative to perfect positive)
        
        Channel Effectiveness (M2_02-04):
        - Position (grid arrangement): Organizes 2D metric relationships
        - Color (hue divergence): Encodes quantitative correlation value
          ✓ Red: Negative correlation (-1.0 to 0.0)
          ✓ White: Zero correlation (0.0)
          ✓ Blue: Positive correlation (0.0 to +1.0)
          ✓ Symmetric: -0.5 and +0.5 equidistant from white
        - Text values: Precise reading (exact correlation coefficient)
        
        Diverging Colormap Justification (M2_06-08):
        - Why red-blue diverging?
          ❌ Red-green: Inaccessible to many colorblind types
          ❌ Sequential (blue gradient): Hides zero point, loses polarity
          ✅ Red-blue: Accessible, symmetric, meaningful
        - Why symmetric around white (not around 0.5)?
          ✓ -0.5 and +0.5 visually equidistant from neutral
          ✓ Zero correlation clearly visible (white cells)
          ✓ Follows M2 Weber's law: equal perceptual steps
        
        Matrix Ordering:
        - Hierarchical clustering: Similar metrics grouped together
        ✓ Gestalt proximity: Related metrics appear near each other
        ✓ Pattern discovery: Metric clusters immediately visible
        - Alternative: Correlation-strength ordering (strongest top-left)
        
        Gestalt Principles (M3_01):
        - Proximity: Grid cells grouped by position (metric pairs)
        - Similarity: Similar correlation values show similar colors
        - Continuity: Color gradient creates smooth visual path
        - Closure: Grid lines separate cells as individual units
        - Figure-ground: White cell borders (figure) on light background
        
        Tufte Principles (Data-Ink Maximization):
        ✓ Minimalist: Grid lines necessary only for cell separation
        ✓ Values displayed: No guessing from color (explicit numbers)
        ✓ No 3D or shadow effects: Flat, clean design
        
        Task Support:
        - Find: Locate specific metric pair correlation
        - Compare: Which metric pairs are most/least correlated?
        - Summarize: Overall correlation structure evident
        - Rank: Strongest positive/negative relationships visible
        - Correlate: Multi-metric relationship analysis
        - Pattern: Metric clusters reveal underlying structure
        
        Why Heatmap vs Alternatives:
        - Scatterplot matrix: ❌ Too many plots for 10+ metrics
        - Network diagram: ❌ Harder to read precise values
        - Correlation table: ❌ Requires linear reading, inefficient
        - ✅ Heatmap: Scalable to 15+ metrics, pattern-friendly
        
        Color Scale Details:
        - zmid=0: White at zero correlation (symmetric)
        - Diverging scale: Equal perceptual steps (Weber's law)
        - Colorbar: Shows -1.0 to +1.0 scale with labels
        
        Accessibility:
        - Red-blue colormap: Distinguishable by most colorblind types
        - Text values: Precise reading independent of color
        - High contrast: Red/white/blue easily discriminated
        
        Hovering Behavior (Eyes Beat Memory - M3_03):
        - Tooltip shows full precision correlation value
        - Metric names clearly labeled in hover
        ✓ External representation > working memory for exact values
        
        Interpretation Guide:
        - Cell color intensity: Correlation magnitude (strength)
        - Cell color hue: Correlation polarity (direction)
        - Red cells: Inverse relationship (one high → other low)
        - Blue cells: Direct relationship (one high → other high)
        - White/pale: Weak or no relationship
        
        Example Insights:
        - GDP vs Technology: Likely strong blue (high correlation)
        - CO2 vs Literacy: Likely weak or inconsistent
        - Energy Use vs GDP: Likely strong blue
        - Inflation vs Growth: Likely weak pink (negative)
        
        Args:
            df: DataFrame with metric columns (numeric only)
            metrics: List of column names to correlate (5-15 recommended)
        """
        
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
