"""
Application Configuration
Production-ready settings for the Global Insights Explorer
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Application settings
class Config:
    """Base configuration"""
    APP_NAME = "Global Insights Explorer"
    VERSION = "1.0.0"
    
    # Server
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 8050))
    
    # Data paths
    DATA_PATH = BASE_DIR / os.getenv('DATA_PATH', 'Dataset')
    ASSETS_PATH = BASE_DIR / 'assets'
    CACHE_DIR = BASE_DIR / '.cache'
    
    # Cache settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'filesystem')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 3600))
    
    # Mapbox
    MAPBOX_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN', '')
    
    # Color schemes
    COLOR_SCHEMES = {
        'economy': {
            'low': '#fee5d9',
            'mid': '#fc8d59',
            'high': '#b30000',
            'scale': 'Reds'
        },
        'environment': {
            'low': '#edf8e9',
            'mid': '#74c476',
            'high': '#005a32',
            'scale': 'Greens'
        },
        'demographics': {
            'low': '#f0f0f0',
            'mid': '#9e9ac8',
            'high': '#54278f',
            'scale': 'Purples'
        },
        'energy': {
            'low': '#fff7bc',
            'mid': '#fe9929',
            'high': '#8c2d04',
            'scale': 'YlOrBr'
        },
        'infrastructure': {
            'low': '#deebf7',
            'mid': '#6baed6',
            'high': '#08519c',
            'scale': 'Blues'
        }
    }
    
    # Chart templates
    CHART_TEMPLATE = 'plotly_white'
    
    # Performance
    MAX_COUNTRIES_COMPARISON = 8
    MAP_ANIMATION_DURATION = 800
    
    @classmethod
    def init_app(cls):
        """Initialize application directories"""
        cls.CACHE_DIR.mkdir(exist_ok=True)
        cls.ASSETS_PATH.mkdir(exist_ok=True)
        return cls


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    CACHE_DEFAULT_TIMEOUT = 7200


# Select config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

APP_CONFIG = config[os.getenv('APP_ENV', 'default')]
