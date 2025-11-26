"""
Global Insights Explorer - Main Application Entry Point
Production-ready Dash application with advanced visualizations
"""
import dash
import dash_bootstrap_components as dbc
import logging
from pathlib import Path

from src.config import APP_CONFIG
from src.utils.data_processor import DataProcessor
from src.utils.visualizations import VisualizationFactory
from src.layouts.main_layout import create_layout
from src.callbacks.app_callbacks import register_callbacks

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configuration
config = APP_CONFIG.init_app()

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700&display=swap'
    ],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)

app.title = "Global Insights Explorer"
server = app.server

# Load and process data
logger.info("Loading and processing data...")
processor = DataProcessor(config.DATA_PATH)
merged_data = processor.merge_datasets()
metrics_info = processor.get_metric_info()
country_list = processor.get_country_list()

# Initialize visualization factory
viz_factory = VisualizationFactory(config)

# Set layout
app.layout = create_layout(merged_data, metrics_info, country_list)

# Register callbacks
register_callbacks(app, merged_data, metrics_info, viz_factory)

if __name__ == '__main__':
    logger.info(f"Starting {config.APP_NAME} v{config.VERSION}")
    logger.info(f"Running on http://{config.HOST}:{config.PORT}")
    
    app.run_server(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )
