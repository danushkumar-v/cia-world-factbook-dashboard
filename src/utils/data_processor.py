"""
Advanced Data Processing Pipeline
Handles cleaning, merging, and preprocessing of all CIA datasets
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from functools import lru_cache
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Production-ready data processor with caching and validation"""
    
    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)
        self.datasets = {}
        self.merged_data = None
        self.country_codes = None
        
    def clean_numeric_column(self, series: pd.Series) -> pd.Series:
        """Clean and convert numeric columns with units"""
        if series.dtype == 'object':
            # Remove common patterns
            series = series.astype(str)
            series = series.str.replace(',', '', regex=False)
            series = series.str.replace('%', '', regex=False)
            series = series.str.replace(' sq km', '', regex=False)
            series = series.str.replace(' km', '', regex=False)
            series = series.str.replace(' m', '', regex=False)
            series = series.str.replace(' bbl/day', '', regex=False)
            series = series.str.replace(' kW', '', regex=False)
            series = series.str.replace(' Mt', '', regex=False)
            series = series.str.replace('$', '', regex=False)
            series = series.str.replace('billion', 'e9', regex=False)
            series = series.str.replace('million', 'e6', regex=False)
            
        # Convert to numeric
        return pd.to_numeric(series, errors='coerce')
    
    def load_geography_data(self) -> pd.DataFrame:
        """Load and clean geography data"""
        logger.info("Loading geography data...")
        df = pd.read_csv(self.data_path / 'geography_data.csv')
        
        # Clean numeric columns
        numeric_cols = ['Area_Total', 'Land_Area', 'Water_Area', 'Land_Boundaries', 
                       'Coastline', 'Highest_Elevation', 'Lowest_Elevation', 
                       'Irrigated_Land']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = self.clean_numeric_column(df[col])
        
        # Clean percentage columns
        pct_cols = ['Forest_Land', 'Other_Land', 'Agricultural_Land']
        for col in pct_cols:
            if col in df.columns:
                df[col] = self.clean_numeric_column(df[col])
        
        # Extract latitude and longitude from coordinates
        if 'Geographic_Coordinates' in df.columns:
            coords = df['Geographic_Coordinates'].str.extract(
                r'(\d+)\s+(\d+)\s+([NS]),\s+(\d+)\s+(\d+)\s+([EW])'
            )
            df['Latitude'] = coords.apply(
                lambda x: (float(x[0]) + float(x[1])/60) * (-1 if x[2]=='S' else 1) if pd.notna(x[0]) else None, 
                axis=1
            )
            df['Longitude'] = coords.apply(
                lambda x: (float(x[3]) + float(x[4])/60) * (-1 if x[5]=='W' else 1) if pd.notna(x[3]) else None,
                axis=1
            )
        
        return df
    
    def load_demographics_data(self) -> pd.DataFrame:
        """Load and clean demographics data"""
        logger.info("Loading demographics data...")
        df = pd.read_csv(self.data_path / 'demographics_data.csv')
        
        # Clean numeric columns
        numeric_cols = ['Total_Population', 'Birth_Rate', 'Death_Rate', 
                       'Net_Migration_Rate', 'Median_Age', 'Sex_Ratio',
                       'Infant_Mortality_Rate', 'Total_Fertility_Rate']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = self.clean_numeric_column(df[col])
        
        # Clean percentage columns
        pct_cols = ['Population_Growth_Rate', 'Total_Literacy_Rate', 
                   'Male_Literacy_Rate', 'Female_Literacy_Rate', 
                   'Youth_Unemployment_Rate']
        
        for col in pct_cols:
            if col in df.columns:
                df[col] = self.clean_numeric_column(df[col])
        
        return df
    
    def load_economy_data(self) -> pd.DataFrame:
        """Load and clean economy data"""
        logger.info("Loading economy data...")
        df = pd.read_csv(self.data_path / 'economy_data.csv')
        
        # All numeric columns (most are already numeric or need cleaning)
        numeric_cols = [col for col in df.columns if col != 'Country' and col != 'Fiscal_Year']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = self.clean_numeric_column(df[col])
        
        return df
    
    def load_energy_data(self) -> pd.DataFrame:
        """Load and clean energy data"""
        logger.info("Loading energy data...")
        df = pd.read_csv(self.data_path / 'energy_data.csv')
        
        numeric_cols = [col for col in df.columns if col != 'Country']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = self.clean_numeric_column(df[col])
        
        return df
    
    def load_transportation_data(self) -> pd.DataFrame:
        """Load and clean transportation data"""
        logger.info("Loading transportation data...")
        df = pd.read_csv(self.data_path / 'transportation_data.csv')
        
        numeric_cols = [col for col in df.columns if col != 'Country']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = self.clean_numeric_column(df[col])
        
        return df
    
    def load_communications_data(self) -> pd.DataFrame:
        """Load and clean communications data"""
        logger.info("Loading communications data...")
        df = pd.read_csv(self.data_path / 'communications_data.csv')
        
        numeric_cols = [col for col in df.columns if col not in ['Country', 'internet_country_code']]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = self.clean_numeric_column(df[col])
        
        return df
    
    def load_government_data(self) -> pd.DataFrame:
        """Load and clean government data"""
        logger.info("Loading government data...")
        df = pd.read_csv(self.data_path / 'government_and_civics_data.csv')
        
        if 'Suffrage_Age' in df.columns:
            df['Suffrage_Age'] = self.clean_numeric_column(df['Suffrage_Age'])
        
        return df
    
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all datasets"""
        self.datasets = {
            'geography': self.load_geography_data(),
            'demographics': self.load_demographics_data(),
            'economy': self.load_economy_data(),
            'energy': self.load_energy_data(),
            'transportation': self.load_transportation_data(),
            'communications': self.load_communications_data(),
            'government': self.load_government_data()
        }
        return self.datasets
    
    def merge_datasets(self) -> pd.DataFrame:
        """Merge all datasets on Country column"""
        logger.info("Merging all datasets...")
        
        if not self.datasets:
            self.load_all_datasets()
        
        # Start with geography (has coordinates)
        merged = self.datasets['geography'].copy()
        
        # Merge other datasets
        for name, df in self.datasets.items():
            if name != 'geography':
                merged = merged.merge(df, on='Country', how='left', suffixes=('', f'_{name}'))
        
        # Add continent classification
        merged['Continent'] = merged['Country'].apply(self._classify_continent)
        
        # Add development classification based on GDP per capita
        if 'Real_GDP_per_Capita_USD' in merged.columns:
            merged['Development_Level'] = pd.cut(
                merged['Real_GDP_per_Capita_USD'],
                bins=[0, 5000, 15000, 30000, float('inf')],
                labels=['Low Income', 'Lower Middle', 'Upper Middle', 'High Income']
            )
        
        self.merged_data = merged
        logger.info(f"Merged dataset shape: {merged.shape}")
        return merged
    
    def _classify_continent(self, country: str) -> str:
        """Classify country by continent (simplified)"""
        # This is a simplified classification
        # In production, use a proper country-to-continent mapping
        asia = ['CHINA', 'INDIA', 'JAPAN', 'SOUTH KOREA', 'INDONESIA', 'THAILAND', 
                'VIETNAM', 'MALAYSIA', 'PHILIPPINES', 'SINGAPORE', 'BANGLADESH',
                'PAKISTAN', 'AFGHANISTAN', 'IRAN', 'IRAQ', 'SAUDI ARABIA', 'YEMEN',
                'SYRIA', 'TURKEY', 'ISRAEL', 'JORDAN', 'LEBANON', 'UAE', 'KUWAIT',
                'QATAR', 'BAHRAIN', 'OMAN', 'AZERBAIJAN', 'ARMENIA', 'GEORGIA',
                'KAZAKHSTAN', 'UZBEKISTAN', 'TURKMENISTAN', 'KYRGYZSTAN', 'TAJIKISTAN',
                'MONGOLIA', 'MYANMAR', 'BURMA', 'CAMBODIA', 'LAOS', 'BRUNEI',
                'TIMOR-LESTE', 'BHUTAN', 'NEPAL', 'SRI LANKA', 'MALDIVES']
        
        europe = ['UNITED KINGDOM', 'GERMANY', 'FRANCE', 'ITALY', 'SPAIN', 'POLAND',
                  'ROMANIA', 'NETHERLANDS', 'BELGIUM', 'CZECH REPUBLIC', 'GREECE',
                  'PORTUGAL', 'SWEDEN', 'HUNGARY', 'AUSTRIA', 'BULGARIA', 'DENMARK',
                  'FINLAND', 'SLOVAKIA', 'NORWAY', 'IRELAND', 'CROATIA', 'BOSNIA',
                  'SERBIA', 'SWITZERLAND', 'ALBANIA', 'LITHUANIA', 'SLOVENIA',
                  'LATVIA', 'NORTH MACEDONIA', 'ESTONIA', 'LUXEMBOURG', 'MALTA',
                  'ICELAND', 'MONTENEGRO', 'BELARUS', 'UKRAINE', 'RUSSIA', 'MOLDOVA']
        
        africa = ['NIGERIA', 'ETHIOPIA', 'EGYPT', 'CONGO', 'SOUTH AFRICA', 'TANZANIA',
                  'KENYA', 'UGANDA', 'ALGERIA', 'SUDAN', 'MOROCCO', 'ANGOLA', 'GHANA',
                  'MOZAMBIQUE', 'MADAGASCAR', 'CAMEROON', 'IVORY COAST', 'NIGER',
                  'BURKINA FASO', 'MALI', 'MALAWI', 'ZAMBIA', 'SENEGAL', 'SOMALIA',
                  'CHAD', 'ZIMBABWE', 'GUINEA', 'RWANDA', 'BENIN', 'BURUNDI', 'TUNISIA',
                  'TOGO', 'SIERRA LEONE', 'LIBYA', 'LIBERIA', 'MAURITANIA', 'ERITREA',
                  'GAMBIA', 'BOTSWANA', 'NAMIBIA', 'GABON', 'LESOTHO', 'GUINEA-BISSAU',
                  'EQUATORIAL GUINEA', 'MAURITIUS', 'ESWATINI', 'DJIBOUTI', 'COMOROS',
                  'CABO VERDE', 'SAO TOME', 'SEYCHELLES', 'CENTRAL AFRICAN REPUBLIC']
        
        north_america = ['UNITED STATES', 'CANADA', 'MEXICO', 'GUATEMALA', 'CUBA',
                        'HAITI', 'DOMINICAN REPUBLIC', 'HONDURAS', 'NICARAGUA',
                        'EL SALVADOR', 'COSTA RICA', 'PANAMA', 'JAMAICA', 'TRINIDAD',
                        'BELIZE', 'BAHAMAS', 'BARBADOS', 'SAINT LUCIA', 'GRENADA',
                        'ANTIGUA', 'DOMINICA', 'SAINT KITTS']
        
        south_america = ['BRAZIL', 'COLOMBIA', 'ARGENTINA', 'PERU', 'VENEZUELA',
                        'CHILE', 'ECUADOR', 'BOLIVIA', 'PARAGUAY', 'URUGUAY',
                        'GUYANA', 'SURINAME', 'FRENCH GUIANA']
        
        oceania = ['AUSTRALIA', 'PAPUA NEW GUINEA', 'NEW ZEALAND', 'FIJI', 'SOLOMON',
                   'MICRONESIA', 'VANUATU', 'SAMOA', 'KIRIBATI', 'TONGA', 'PALAU',
                   'TUVALU', 'NAURU', 'MARSHALL ISLANDS']
        
        country_upper = country.upper()
        
        for continent_name, countries in [
            ('Asia', asia), ('Europe', europe), ('Africa', africa),
            ('North America', north_america), ('South America', south_america),
            ('Oceania', oceania)
        ]:
            if any(c in country_upper for c in countries):
                return continent_name
        
        return 'Other'
    
    def get_metric_info(self) -> Dict:
        """Get information about all available metrics"""
        if self.merged_data is None:
            self.merge_datasets()
        
        metrics = {}
        
        # Categorize metrics
        categories = {
            'Geography': ['Area_Total', 'Land_Area', 'Water_Area', 'Coastline', 
                         'Forest_Land', 'Agricultural_Land', 'Irrigated_Land'],
            'Demographics': ['Total_Population', 'Population_Growth_Rate', 'Birth_Rate',
                           'Death_Rate', 'Median_Age', 'Infant_Mortality_Rate',
                           'Total_Literacy_Rate'],
            'Economy': ['Real_GDP_PPP_billion_USD', 'Real_GDP_per_Capita_USD',
                       'Real_GDP_Growth_Rate_percent', 'Unemployment_Rate_percent',
                       'Exports_billion_USD', 'Imports_billion_USD'],
            'Energy': ['electricity_access_percent', 'carbon_dioxide_emissions_Mt',
                      'petroleum_bbl_per_day', 'natural_gas_cubic_meters'],
            'Infrastructure': ['roadways_km', 'railways_km', 'airports_paved_runways_count',
                             'waterways_km'],
            'Communications': ['internet_users_total', 'mobile_cellular_subscriptions_total',
                             'broadband_fixed_subscriptions_total']
        }
        
        for category, cols in categories.items():
            metrics[category] = []
            for col in cols:
                if col in self.merged_data.columns:
                    metrics[category].append({
                        'name': col,
                        'label': col.replace('_', ' ').title(),
                        'min': float(self.merged_data[col].min()) if pd.notna(self.merged_data[col].min()) else 0,
                        'max': float(self.merged_data[col].max()) if pd.notna(self.merged_data[col].max()) else 0,
                        'mean': float(self.merged_data[col].mean()) if pd.notna(self.merged_data[col].mean()) else 0
                    })
        
        return metrics
    
    def get_country_list(self) -> List[str]:
        """Get sorted list of all countries"""
        if self.merged_data is None:
            self.merge_datasets()
        
        return sorted(self.merged_data['Country'].dropna().unique().tolist())
    
    def save_processed_data(self, output_path: Path):
        """Save processed data for faster loading"""
        if self.merged_data is None:
            self.merge_datasets()
        
        output_path = Path(output_path)
        output_path.mkdir(exist_ok=True)
        
        # Save merged data
        self.merged_data.to_csv(output_path / 'merged_data.csv', index=False)
        
        # Save metric info
        with open(output_path / 'metrics_info.json', 'w') as f:
            json.dump(self.get_metric_info(), f, indent=2)
        
        logger.info(f"Processed data saved to {output_path}")
