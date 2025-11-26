"""
Data Export Utilities
Export processed data and visualizations
"""
import pandas as pd
from pathlib import Path
from typing import Optional
import json
import plotly.graph_objects as go


class DataExporter:
    """Handle data export in various formats"""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_to_csv(self, df: pd.DataFrame, filename: str):
        """Export DataFrame to CSV"""
        filepath = self.output_dir / f"{filename}.csv"
        df.to_csv(filepath, index=False)
        return filepath
    
    def export_to_excel(self, df: pd.DataFrame, filename: str, sheet_name: str = "Data"):
        """Export DataFrame to Excel"""
        filepath = self.output_dir / f"{filename}.xlsx"
        df.to_excel(filepath, sheet_name=sheet_name, index=False)
        return filepath
    
    def export_to_json(self, df: pd.DataFrame, filename: str, orient: str = "records"):
        """Export DataFrame to JSON"""
        filepath = self.output_dir / f"{filename}.json"
        df.to_json(filepath, orient=orient, indent=2)
        return filepath
    
    def export_figure_to_html(self, fig: go.Figure, filename: str):
        """Export Plotly figure to HTML"""
        filepath = self.output_dir / f"{filename}.html"
        fig.write_html(filepath)
        return filepath
    
    def export_figure_to_image(self, fig: go.Figure, filename: str, format: str = "png"):
        """Export Plotly figure to image (requires kaleido)"""
        filepath = self.output_dir / f"{filename}.{format}"
        fig.write_image(str(filepath), format=format, width=1920, height=1080)
        return filepath
    
    def create_data_dictionary(self, metrics_info: dict, filename: str = "data_dictionary"):
        """Create data dictionary JSON"""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(metrics_info, f, indent=2)
        return filepath
    
    def export_summary_report(self, df: pd.DataFrame, metrics: list, filename: str = "summary_report"):
        """Export summary statistics report"""
        summary = {}
        
        for metric in metrics:
            if metric in df.columns:
                series = df[metric].dropna()
                summary[metric] = {
                    'count': int(len(series)),
                    'mean': float(series.mean()),
                    'median': float(series.median()),
                    'std': float(series.std()),
                    'min': float(series.min()),
                    'max': float(series.max()),
                    'q25': float(series.quantile(0.25)),
                    'q75': float(series.quantile(0.75))
                }
        
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return filepath
