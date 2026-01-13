# 🌍 Global Insights Explorer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/Dash-2.14+-green.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready, interactive data visualization web application for exploring CIA World Factbook-style datasets across ~250+ countries/territories.

## ✨ Features

- 🗺️ **Advanced Maps**: Choropleth maps, 3D globe visualizations, sunburst charts
- 🌓 **Light/Dark Theme**: Theme toggle with theme-aware Plotly styling
- 📊 **Interactive Analytics**: Comparisons, correlation analysis, regional insights  
- 🎨 **Professional Design**: Modern UI with custom gradients and animations
- ⚡ **High Performance**: Optimized data processing with caching
- 📱 **Responsive**: Works on desktop, tablet, and mobile

## 🚀 Quick Start

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

## 📊 Data Coverage

- **~258+** Countries/Territories (after cleaning; depends on the input CSVs)
- **7** Data Domains (Geography, Demographics, Economy, Energy, Transportation, Communications, Government)
- **100+** Metrics
- **Source**: CIA World Factbook 2024-2025

## 📁 Project Structure

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

## 🎨 Visualizations

- **Choropleth Maps** - Country-level color coding
- **3D Globe** - Interactive rotating Earth
- **Radar Charts** - Multi-metric comparisons (best with 3–8 metrics; normalized)
- **Scatter Plots** - Correlation analysis with trendlines
- **Regional Bars** - Continental aggregations
- **Distributions** - Histogram / Box / Violin views for a metric
- **Sunburst Charts** - Hierarchical visualizations
- **Heatmaps** - Correlation matrices

## 🛠️ Technology Stack

- **Framework**: Dash, Plotly, Flask
- **UI**: Dash Bootstrap Components
- **Data**: Pandas, NumPy
- **Visualization**: Plotly Express, Plotly Graph Objects
- **Deployment**: Gunicorn, Docker

## 📖 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Visualization Guide](docs/VISUALIZATION_GUIDE.md)
- [Full Documentation](docs/README.md)

## ✅ Tests

```powershell
python -m pytest -q
```

## 🧯 Troubleshooting

- If the app fails to start, run the safer runner for a full traceback: `python run_app.py`
- If you suspect stale cached data, clear the cache folder (if present): `Remove-Item -Recurse -Force .cache -ErrorAction SilentlyContinue`

## 🚀 Deployment

### Docker
```bash
docker build -t global-insights .
docker run -p 8050:8050 global-insights
```

### Production Server
```powershell
waitress-serve --host=127.0.0.1 --port=8050 app:server
```

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Data: CIA World Factbook 2024-2025
- Built with Dash, Plotly, and Python

---

**Made with ❤️ for data visualization**
