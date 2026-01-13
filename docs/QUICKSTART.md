# 🚀 Quick Start Guide

## Installation (5 minutes)

### Option 1: Automated Setup (Recommended)
```powershell
# Run the automated setup script
\.\scripts\start.ps1
```

### Option 2: Manual Setup
```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

### Option 3: Docker
```powershell
# Build and run with Docker
docker build -t global-insights .
docker run -p 8050:8050 global-insights
```

---

## 🎯 First Steps After Launch

1. **Open your browser** → http://localhost:8050

2. **Explore the Dashboard:**
   - See global statistics at the top
   - Use the left sidebar to select data domains
   - Choose different visualization types
   - Apply filters for focused analysis

3. **Try These Quick Examples:**

   **Example 1: GDP Map**
   - Domain: Economy
   - Metric: Real GDP per Capita
   - Viz Type: Choropleth Map
   - Color: Blues
   - Click "Apply"

   **Example 2: Internet vs GDP**
   - Go to "Correlation" tab
   - X-Axis: Real GDP per Capita USD
   - Y-Axis: Internet Users Total
   - Color By: Continent
   - Click "Generate Scatter Plot"

   **Example 3: Country Comparison**
   - Go to "Compare" tab
   - Select: USA, China, India, Germany
   - Metrics: Select 3–8 metrics (e.g., Total_Population, Real_GDP_per_Capita_USD, internet_users_total)
   - Chart Type: Radar Chart
   - Click "Compare Countries"

---

## 📊 Data Domains & Key Metrics

### 🌍 Geography
- `Area_Total` - Total land area
- `Coastline` - Coastline length
- `Forest_Land` - Forest coverage percentage
- `Agricultural_Land` - Agricultural land percentage

### 👥 Demographics
- `Total_Population` - Population count
- `Population_Growth_Rate` - Annual growth rate
- `Median_Age` - Median age of population
- `Total_Literacy_Rate` - Literacy percentage

### 💰 Economy
- `Real_GDP_per_Capita_USD` - GDP per person
- `Real_GDP_Growth_Rate_percent` - GDP growth
- `Unemployment_Rate_percent` - Unemployment
- `Exports_billion_USD` - Export value
- `Imports_billion_USD` - Import value

### ⚡ Energy
- `electricity_access_percent` - Electricity access
- `carbon_dioxide_emissions_Mt` - CO2 emissions
- `petroleum_bbl_per_day` - Oil production
- `natural_gas_cubic_meters` - Gas production

### 🚗 Transportation
- `roadways_km` - Total road length
- `railways_km` - Railway network
- `airports_paved_runways_count` - Paved airports

### 🌐 Communications
- `internet_users_total` - Internet users
- `mobile_cellular_subscriptions_total` - Mobile subscriptions
- `broadband_fixed_subscriptions_total` - Broadband users

### 🏛️ Government
- `Capital` - Capital city
- `Government_Type` - Type of government
- `Suffrage_Age` - Voting age

---

## 🎨 Visualization Types

| Type | Best For | Features |
|------|----------|----------|
| 🗺️ **Choropleth Map** | Global distribution | Color-coded countries, multiple projections |
| 🌐 **3D Globe** | Presentations | Interactive rotating globe, bubble markers |
| ☀️ **Sunburst** | Hierarchical data | Continent → Country drill-down |
| 📊 **Regional Bars** | Continental comparison | Aggregated statistics by region |
| 🕸️ **Radar Chart** | Country comparison | Multi-metric normalized view |
| 📈 **Scatter Plot** | Correlations | Trendlines, statistical analysis |

---

## 🎛️ Control Panel Guide

### Domain Selector
Choose the category of data you want to explore

### Metric Selector
Pick the specific measurement within that domain

### Visualization Type
Select how you want to see the data:
- Maps for geographic distribution
- Charts for comparisons and trends

### Color Scheme
Choose colors that best represent your data:
- **Blues**: Economic data, water-related
- **Reds**: High-impact metrics, warnings
- **Greens**: Environmental, positive trends
- **Viridis/Plasma**: Scientific data
- **Rainbow**: Maximum color variation

### Continent Filter
Focus on specific regions:
- Select multiple continents
- Leave empty for global view

### Development Level
Filter by economic classification:
- High Income
- Upper Middle Income
- Lower Middle Income
- Low Income

---

## 💡 Pro Tips

### Performance
- Filter data before creating complex visualizations
- Use regional aggregations for large datasets
- Close unused tabs to free memory

### Analysis
- Start with maps for overview
- Use scatter plots to find correlations
- Compare similar countries with radar charts
- Export data for deeper analysis in Excel/Python

### Presentation
- Use 3D globe for dramatic effect
- Sunburst charts tell hierarchical stories
- Export high-resolution images for reports
- Consistent color schemes across charts

### Customization
- Edit `.env` file for custom settings
- Modify `config.py` for color schemes
- Add custom metrics in `data_processor.py`

---

## 🔧 Troubleshooting

### App won't start
```powershell
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
netstat -ano | findstr :8050
```

### Data not loading
- Ensure all CSV files are in the `Dataset/` folder
- Check file permissions
- Look for error messages in the console

### Slow performance
- Close other applications
- Clear browser cache
- Restart the application
- Use smaller datasets for testing

### Visualizations not showing
- Check browser console (F12)
- Try a different browser
- Disable browser extensions
- Update to latest Plotly version

---

## 📚 Learning Resources

### Inside the App
- Hover over charts for tooltips
- Click on map regions for details
- Use zoom and pan controls
- Try all visualization types

### Documentation
- `README.md` - Full documentation
- `VISUALIZATION_GUIDE.md` - Detailed visual examples
- Code comments - Inline explanations

### Data Source
- [CIA World Factbook](https://www.cia.gov/the-world-factbook/)
- 259 countries and territories
- 7 data domains
- 100+ metrics

---

## 🎯 Common Use Cases

### Academic Research
```
1. Select your research domain
2. Choose relevant metrics
3. Filter by region or development level
4. Export data for analysis
5. Generate publication-quality charts
```

### Business Intelligence
```
1. Compare target markets
2. Analyze economic indicators
3. Assess infrastructure readiness
4. Export reports for stakeholders
```

### Data Journalism
```
1. Find interesting correlations
2. Create compelling visualizations
3. Export high-res images
4. Support stories with data
```

### Policy Making
```
1. Regional comparisons
2. Development tracking
3. Resource allocation insights
4. Evidence-based decisions
```

---

## 🚀 Next Steps

### Beginner
1. ✅ Install and run the app
2. ✅ Try the example visualizations
3. ✅ Explore different metrics
4. ✅ Experiment with filters

### Intermediate
1. ⭐ Create custom comparisons
2. ⭐ Analyze correlations
3. ⭐ Export data and charts
4. ⭐ Customize color schemes

### Advanced
1. 🔥 Modify the code
2. 🔥 Add new metrics
3. 🔥 Create custom visualizations
4. 🔥 Deploy to production

---

## 📞 Support

- **Issues**: Check console for error messages
- **Features**: Suggest in project repository
- **Questions**: Refer to documentation
- **Updates**: Check for new versions

---

**Happy Exploring! 🌍📊**
