# Global Insights Explorer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/Dash-2.14+-green.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready, interactive data visualization web application for exploring CIA World Factbook datasets across more than 250 countries and territories.

## Live Deployment

**Access the live application:** [https://cia-world-factbook-dashboard.onrender.com/](https://cia-world-factbook-dashboard.onrender.com/)

**Note:** The deployment is hosted on a free-tier service and may enter sleep mode after periods of inactivity. If you encounter a loading delay, please wait approximately 50 seconds for the service to wake up and initialize. Subsequent visits will load normally.

## Features

- **Advanced Mapping Visualizations**: Choropleth maps, 3D globe visualizations, and sunburst charts for geospatial data exploration
- **Theme Customization**: Light and dark theme toggle with theme-aware Plotly styling for optimal viewing experience
- **Interactive Analytics**: Multi-dimensional comparisons, correlation analysis, and regional insights across datasets
- **Professional Design**: Modern user interface with custom gradients, animations, and responsive layouts
- **High Performance**: Optimized data processing with caching mechanisms for improved load times
- **Cross-Platform Compatibility**: Responsive design that works seamlessly on desktop, tablet, and mobile devices

## Quick Start

### Installation

```powershell
# Clone the repository
git clone <repository-url>
cd Project

# Run setup script (recommended)
\.\scripts\start.ps1

# OR (manual) create a venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Conda (optional)
If you prefer Conda:

```powershell
conda create -n cia-env python=3.11 -y
conda activate cia-env
pip install -r requirements.txt
python app.py
```

### Access the App
Open your browser: **http://localhost:8050**

## Data Coverage

The application provides comprehensive global data coverage:

- **Geographic Coverage**: Approximately 258+ countries and territories (after data cleaning; final count depends on input CSV files)
- **Data Domains**: 7 major domains including Geography, Demographics, Economy, Energy, Transportation, Communications, and Government
- **Metrics**: Over 100 individual metrics across all domains
- **Data Source**: CIA World Factbook (2024-2025 edition)

## Project Structure

```
Project/
├── app.py                      # Main application entry point
├── src/
│   ├── config.py              # Configuration settings
│   ├── components/            # Reusable UI components
│   │   └── ui_components.py
│   ├── layouts/               # Page layouts
│   │   └── main_layout.py
│   ├── callbacks/             # Dash callbacks
│   │   └── app_callbacks.py
│   └── utils/                 # Utility modules
│       ├── data_processor.py  # Data processing
│       ├── visualizations.py  # Chart factories
│       ├── utils.py          # Helper functions
│       └── export_utils.py   # Export utilities
├── assets/                    # CSS and static assets
│   └── styles.css
├── Dataset/                   # Data files
├── docs/                      # Documentation
│   ├── README.md
│   ├── QUICKSTART.md
│   └── VISUALIZATION_GUIDE.md
├── scripts/                   # Utility scripts
│   └── start.ps1
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
└── .gitignore                # Git ignore rules
```

## Visualization Types

- **Choropleth Maps**: Country-level color-coded visualizations displaying geographic distributions
- **3D Globe**: Interactive rotating Earth model with real-time data overlays
- **Radar Charts**: Multi-metric comparisons optimized for 3-8 normalized metrics
- **Scatter Plots**: Correlation analysis with statistical trendlines and confidence intervals
- **Regional Bar Charts**: Continental and regional data aggregations
- **Distribution Charts**: Histogram, box plot, and violin plot representations for metric distributions
- **Sunburst Charts**: Hierarchical visualizations showing data relationships across multiple levels
- **Heatmaps**: Correlation matrices displaying relationships between multiple variables

## Technology Stack

- **Web Framework**: Dash (by Plotly), Flask
- **User Interface**: Dash Bootstrap Components
- **Data Processing**: Pandas, NumPy
- **Visualization Libraries**: Plotly Express, Plotly Graph Objects
- **Deployment Solutions**: Gunicorn (WSGI server), Docker containerization

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md) - Step-by-step installation and setup instructions
- [Visualization Guide](docs/VISUALIZATION_GUIDE.md) - Detailed guide on creating and customizing visualizations
- [Full Documentation](docs/README.md) - Complete technical documentation

## Testing

```powershell
python -m pytest -q
```

## Troubleshooting

**Application Startup Issues:**
- If the application fails to start, use the alternative runner for detailed error traceback: `python run_app.py`

**Cache-Related Issues:**
- If you experience stale or corrupted cached data, clear the cache directory using: `Remove-Item -Recurse -Force .cache -ErrorAction SilentlyContinue`

**Port Conflicts:**
- If port 8050 is already in use, modify the port in `src/config.py` or set the PORT environment variable

## Deployment

### Docker
```bash
docker build -t global-insights .
docker run -p 8050:8050 global-insights
```

### Production Server
```powershell
waitress-serve --host=127.0.0.1 --port=8050 app:server
```

## Contributing

Contributions are welcome and appreciated. Please read our contributing guidelines before submitting pull requests. Ensure that all code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the LICENSE file for complete details.

## Acknowledgments

- **Data Source**: CIA World Factbook (2024-2025 edition)
- **Development Framework**: Dash by Plotly
- **Visualization Libraries**: Plotly Express and Plotly Graph Objects
- **Python Libraries**: Pandas, NumPy, Flask

---

**Developed for advanced data visualization and global insights analytics**
