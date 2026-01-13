# Global Insights Explorer

A production-ready, interactive data visualization web application for exploring CIA World Factbook data across 259 countries.

## 🌟 Features

- **🗺️ Advanced Maps**: Beautiful choropleth maps, 3D globe visualizations, and animated geospatial analytics
- **📊 Interactive Analytics**: Multi-dimensional comparisons, correlation analysis, and regional insights
- **🎨 Professional Design**: Modern UI with custom color schemes, gradients, and animations
- **⚡ High Performance**: Optimized data processing with caching and lazy loading
- **📱 Responsive**: Works seamlessly on desktop, tablet, and mobile devices

## 📊 Data Domains

- **Geography**: Area, land use, elevation, coastlines
- **Demographics**: Population, growth rates, literacy, age distribution
- **Economy**: GDP, trade, unemployment, poverty levels
- **Energy**: Electricity, fuel consumption, carbon emissions
- **Transportation**: Roads, railways, airports, pipelines
- **Communications**: Internet, mobile, broadband penetration
- **Government**: Political structure, capital cities, voting age

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone or navigate to the project directory**

```powershell
cd "d:\MS DSAI\JBI100 Visualization\Project"
```

2. **Create a virtual environment** (recommended)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

4. **Set up environment variables** (optional)

```powershell
cp .env.example .env
# Edit .env file with your settings
```

### Running the Application

**Development Mode:**

```powershell
python app.py
```

**Production Mode:**

```powershell
$env:APP_ENV="production"; python app.py
```

The application will be available at `http://localhost:8050`

## 📁 Project Structure

```
Project/
├── app.py                      # Main Dash application
├── run_app.py                  # Safer runner with traceback output
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── assets/
│   └── styles.css             # Custom CSS styling
├── scripts/
│   └── start.ps1               # Windows setup + launch script
├── Dataset/
│   ├── geography_data.csv
│   ├── demographics_data.csv
│   ├── economy_data.csv
│   ├── energy_data.csv
│   ├── transportation_data.csv
│   ├── communications_data.csv
│   └── government_and_civics_data.csv
├── src/
│   ├── config.py               # App configuration
│   ├── callbacks/              # Dash callbacks
│   ├── components/             # Reusable UI components
│   ├── layouts/                # Page layouts
│   └── utils/                  # Data processing + visualization utilities
└── .cache/                     # Cached processed data (optional)
```

## 🎨 Visualization Types

### Maps
- **Choropleth Maps**: Color-coded countries based on metrics
- **3D Globe**: Interactive spherical visualization
- **Bubble Maps**: Size-encoded country metrics

### Charts
- **Radar Charts**: Multi-dimensional country comparison
- **Scatter Plots**: Correlation analysis with trendlines
- **Bar Charts**: Regional comparisons
- **Sunburst Charts**: Hierarchical data exploration
- **Heatmaps**: Correlation matrices

## 🛠️ Configuration

Edit `config.py` or `.env` file to customize:

- **PORT**: Application port (default: 8050)
- **DEBUG**: Debug mode (default: True for development)
- **CACHE_TYPE**: Cache backend (filesystem/redis)
- **MAPBOX_TOKEN**: Optional Mapbox access token for enhanced maps

## 📊 Usage Examples

### 1. Global GDP Comparison
- Select Domain: **Economy**
- Select Metric: **Real GDP per Capita**
- Visualization: **Choropleth Map**
- Color Scheme: **Blues**

### 2. Internet Penetration Analysis
- Domain: **Communications**
- Metric: **Internet Users Total**
- Visualization: **3D Globe**

### 3. Country Comparison
- Navigate to **Compare** tab
- Select Countries: USA, China, India, Germany
- Select Metrics: GDP, Population, Internet Users
- Chart Type: **Radar Chart**

### 4. Correlation Analysis
- Navigate to **Correlation** tab
- X-Axis: **GDP per Capita**
- Y-Axis: **Internet Users**
- Color By: **Continent**

## 🚀 Production Deployment

### Using Gunicorn (Linux/Mac)

```bash
gunicorn app:server -w 4 -b 0.0.0.0:8050
```

### Using Waitress (Windows)

```powershell
waitress-serve --host=0.0.0.0 --port=8050 app:server
```

### Docker Deployment

```dockerfile
# Build image
docker build -t global-insights-explorer .

# Run container
docker run -p 8050:8050 global-insights-explorer
```

## 🎯 Performance Optimization

- **Caching**: Processed data is cached to reduce load times
- **Lazy Loading**: Charts load on-demand
- **Data Filtering**: Client-side filtering for instant updates
- **Optimized Rendering**: Plotly configuration for smooth animations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Data Source: CIA World Factbook 2024-2025
- Visualization: Plotly & Dash
- Design: Bootstrap & Custom CSS
- Icons: Unicode Emojis

## 📞 Support

For issues or questions, please open an issue on the project repository.

---

**Built with ❤️ using Dash, Plotly, and Python**
