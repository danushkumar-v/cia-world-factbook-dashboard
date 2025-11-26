"""
Utility Functions
Helper functions for data processing and visualization
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import json


def format_number(value: float, precision: int = 2) -> str:
    """Format number with appropriate suffix (K, M, B, T)"""
    if pd.isna(value):
        return "N/A"
    
    abs_value = abs(value)
    
    if abs_value >= 1e12:
        return f"{value/1e12:.{precision}f}T"
    elif abs_value >= 1e9:
        return f"{value/1e9:.{precision}f}B"
    elif abs_value >= 1e6:
        return f"{value/1e6:.{precision}f}M"
    elif abs_value >= 1e3:
        return f"{value/1e3:.{precision}f}K"
    else:
        return f"{value:.{precision}f}"


def calculate_percentile_rank(df: pd.DataFrame, column: str, value: float) -> float:
    """Calculate percentile rank of a value in a column"""
    if pd.isna(value):
        return 0
    
    valid_values = df[column].dropna()
    rank = (valid_values < value).sum() / len(valid_values) * 100
    return rank


def normalize_series(series: pd.Series, method: str = 'minmax') -> pd.Series:
    """Normalize a pandas series"""
    if method == 'minmax':
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return ((series - min_val) / (max_val - min_val)) * 100
    elif method == 'zscore':
        return (series - series.mean()) / series.std()
    else:
        return series


def get_color_from_value(value: float, min_val: float, max_val: float, colorscale: str = 'Blues') -> str:
    """Get color from value based on colorscale"""
    import plotly.colors as pc
    
    if pd.isna(value) or max_val == min_val:
        return '#cccccc'
    
    normalized = (value - min_val) / (max_val - min_val)
    
    # Get colorscale
    if hasattr(pc.sequential, colorscale):
        colors = getattr(pc.sequential, colorscale)
    else:
        colors = pc.sequential.Blues
    
    # Interpolate color
    idx = int(normalized * (len(colors) - 1))
    return colors[idx]


def export_data_to_json(df: pd.DataFrame, filename: str):
    """Export DataFrame to JSON"""
    df.to_json(filename, orient='records', indent=2)


def export_data_to_csv(df: pd.DataFrame, filename: str):
    """Export DataFrame to CSV"""
    df.to_csv(filename, index=False)


def calculate_composite_index(
    df: pd.DataFrame,
    metrics: List[str],
    weights: List[float] = None
) -> pd.Series:
    """
    Calculate composite index from multiple metrics
    
    Args:
        df: DataFrame with metrics
        metrics: List of metric column names
        weights: Optional weights for each metric (must sum to 1)
    
    Returns:
        Series with composite index scores
    """
    if weights is None:
        weights = [1/len(metrics)] * len(metrics)
    
    if len(weights) != len(metrics):
        raise ValueError("Number of weights must match number of metrics")
    
    if abs(sum(weights) - 1.0) > 0.01:
        raise ValueError("Weights must sum to 1")
    
    # Normalize each metric
    normalized_data = pd.DataFrame()
    for metric in metrics:
        normalized_data[metric] = normalize_series(df[metric])
    
    # Calculate weighted sum
    composite = sum(normalized_data[metric] * weight 
                   for metric, weight in zip(metrics, weights))
    
    return composite


def get_top_countries(
    df: pd.DataFrame,
    metric: str,
    n: int = 10,
    ascending: bool = False
) -> pd.DataFrame:
    """Get top N countries by metric"""
    return df.nlargest(n, metric) if not ascending else df.nsmallest(n, metric)


def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate percentage growth rate"""
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return 0
    return ((current - previous) / previous) * 100


def categorize_country(
    gdp_per_capita: float,
    thresholds: Dict[str, float] = None
) -> str:
    """Categorize country by development level"""
    if pd.isna(gdp_per_capita):
        return "Unknown"
    
    if thresholds is None:
        thresholds = {
            'Low Income': 5000,
            'Lower Middle': 15000,
            'Upper Middle': 30000
        }
    
    if gdp_per_capita < thresholds['Low Income']:
        return 'Low Income'
    elif gdp_per_capita < thresholds['Lower Middle']:
        return 'Lower Middle Income'
    elif gdp_per_capita < thresholds['Upper Middle']:
        return 'Upper Middle Income'
    else:
        return 'High Income'


def detect_outliers(series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """
    Detect outliers in a series
    
    Args:
        series: Pandas series
        method: 'iqr' or 'zscore'
        threshold: Threshold for outlier detection
    
    Returns:
        Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (series < lower_bound) | (series > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold
    
    return pd.Series([False] * len(series), index=series.index)


def create_summary_stats(df: pd.DataFrame, metric: str) -> Dict[str, Any]:
    """Create summary statistics for a metric"""
    series = df[metric].dropna()
    
    return {
        'count': int(len(series)),
        'mean': float(series.mean()),
        'median': float(series.median()),
        'std': float(series.std()),
        'min': float(series.min()),
        'max': float(series.max()),
        'q25': float(series.quantile(0.25)),
        'q75': float(series.quantile(0.75)),
        'skewness': float(series.skew()),
        'kurtosis': float(series.kurtosis())
    }
