import pandas as pd
import numpy as np
from pathlib import Path

class FoodPriceDataPreprocessor:
    """
    A class to handle pre-processing and analysis of food price dataset.
    """
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.df_processed = None
        
    def load_csv(self):
        self.df = pd.read_csv(self.filepath)
        print(f"Data loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
        
        return self
    
    def explore_basic_info(self):
        """
        Display basic information about the dataset:
        - Shape, columns, data types
        - Missing value statistics
        - Date range coverage
        """
        print("\n" + "="*60)
        print("DATASET OVERVIEW")
        print("="*60)
        
        # Basic shape information
        print(f"\nShape: {self.df.shape}")
        print(f"Memory usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Geographic coverage
        print(f"\nGeographic Coverage:")
        print(f"  - Countries: {self.df['country'].nunique()}")
        print(f"  - Admin Level 1 regions: {self.df['adm1_name'].nunique()}")
        print(f"  - Markets: {self.df['mkt_name'].nunique()}")
        
        # Date range
        print(f"\nTemporal Coverage:")
        print(f"  - Years: {sorted(self.df['year'].unique())}")
        print(f"  - Date range: {self.df['DATES'].min()} to {self.df['DATES'].max()}")
        
        # Missing values summary
        print("\n" + "-"*60)
        print("MISSING VALUES SUMMARY")
        print("-"*60)
        missing_pct = (self.df.isnull().sum() / len(self.df) * 100).sort_values(ascending=False)
        print(f"\nColumns with >50% missing: {(missing_pct > 50).sum()}")
        print(f"Columns with >90% missing: {(missing_pct > 90).sum()}")
        
        return self
    
    def identify_column_groups(self):
        """
        Categorize columns into logical groups for easier processing:
        - Geographic identifiers (ISO3, country, region, market, coordinates)
        - Temporal identifiers (DATES, year, month)
        - Metadata (currency, components, confidence scores, coverage)
        - Price columns (base food items)
        - Derived metrics (o_, h_, l_, c_, inflation_, trust_ prefixes)
        """
        cols = self.df.columns.tolist()
        
        # Geographic identifiers
        self.geo_cols = ['ISO3', 'country', 'adm1_name', 'adm2_name', 
                         'mkt_name', 'lat', 'lon', 'geo_id']
        
        # Temporal identifiers
        self.time_cols = ['DATES', 'year', 'month']
        
        # Metadata and quality indicators
        self.meta_cols = ['currency', 'components', 'start_dense_data', 
                          'last_survey_point', 'data_coverage', 
                          'data_coverage_recent', 'index_confidence_score', 
                          'spatially_interpolated']
        
        # Base food item price columns (no prefix)
        self.food_cols = [col for col in cols 
                          if not any(col.startswith(prefix) for prefix in 
                                   ['o_', 'h_', 'l_', 'c_', 'inflation_', 'trust_'])
                          and col not in self.geo_cols + self.time_cols + self.meta_cols]
        
        # Derived metric columns with prefixes
        # o_ = original/observed price, h_ = high, l_ = low, c_ = current/closing
        self.derived_cols = {
            'original': [col for col in cols if col.startswith('o_')],
            'high': [col for col in cols if col.startswith('h_')],
            'low': [col for col in cols if col.startswith('l_')],
            'current': [col for col in cols if col.startswith('c_')],
            'inflation': [col for col in cols if col.startswith('inflation_')],
            'trust': [col for col in cols if col.startswith('trust_')]
        }
        
        print("\n" + "="*60)
        print("COLUMN GROUPS")
        print("="*60)
        print(f"Geographic: {len(self.geo_cols)} columns")
        print(f"Temporal: {len(self.time_cols)} columns")
        print(f"Metadata: {len(self.meta_cols)} columns")
        print(f"Base food items: {len(self.food_cols)} columns")
        print(f"Derived metrics:")
        for key, cols in self.derived_cols.items():
            print(f"  - {key}: {len(cols)} columns")
        
        return self
    
    def handle_missing_values(self, strategy='analyze'):
        """
        Handle missing values in the dataset.
        
        Args:
            strategy: 'analyze' (default) - only report missing values
                     'drop' - remove rows with critical missing data
                     'impute' - fill missing numeric values with forward fill
        """
        print("\n" + "="*60)
        print("MISSING VALUE HANDLING")
        print("="*60)
        
        if strategy == 'analyze':
            # Report missing values by column group
            for col in self.geo_cols + self.time_cols:
                missing = self.df[col].isnull().sum()
                if missing > 0:
                    print(f"⚠ {col}: {missing} missing ({missing/len(self.df)*100:.1f}%)")
            
            # Food price columns missing summary
            food_missing = self.df[self.food_cols].isnull().sum()
            print(f"\nFood price columns: {(food_missing > 0).sum()} have missing values")
            
        elif strategy == 'drop':
            # Drop rows where critical identifiers are missing
            critical_cols = ['ISO3', 'country', 'DATES', 'year', 'month']
            initial_len = len(self.df)
            self.df = self.df.dropna(subset=critical_cols)
            print(f"Dropped {initial_len - len(self.df)} rows with missing critical data")
            
        elif strategy == 'impute':
            # Forward fill for time series data (within each geographic group)
            self.df = self.df.sort_values(['geo_id', 'DATES'])
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df.groupby('geo_id')[numeric_cols].fillna(method='ffill')
            print("Applied forward fill imputation for numeric columns")
        
        return self
    
    def convert_data_types(self):
        """
        Convert columns to appropriate data types:
        - DATES to datetime
        - Numeric columns to float/int
        - Categorical columns for geographic identifiers
        """
        print("\n" + "="*60)
        print("DATA TYPE CONVERSION")
        print("="*60)
        
        # Convert DATES to datetime
        self.df['DATES'] = pd.to_datetime(self.df['DATES'], errors='coerce')
        print("✓ Converted DATES to datetime")
        
        # Convert year and month to integers
        self.df['year'] = pd.to_numeric(self.df['year'], errors='coerce').astype('Int64')
        self.df['month'] = pd.to_numeric(self.df['month'], errors='coerce').astype('Int64')
        print("✓ Converted year and month to integers")
        
        # Convert geographic columns to category for memory efficiency
        for col in ['ISO3', 'country', 'adm1_name', 'adm2_name', 'currency']:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype('category')
        print("✓ Converted geographic/currency columns to category")
        
        # Convert coordinates to float
        self.df['lat'] = pd.to_numeric(self.df['lat'], errors='coerce')
        self.df['lon'] = pd.to_numeric(self.df['lon'], errors='coerce')
        print("✓ Converted coordinates to float")
        
        return self
    
    def detect_outliers(self, columns=None, method='iqr', threshold=3):
        """
        Detect outliers in numeric columns using IQR or z-score method.
        
        Args:
            columns: List of columns to check (default: all food price columns)
            method: 'iqr' (interquartile range) or 'zscore'
            threshold: Number of standard deviations (for zscore) or IQR multiplier
        
        Returns:
            self: Returns the preprocessor object for method chaining
        """
        if columns is None:
            columns = self.food_cols[:10]  # Check first 10 food items as example
        
        print("\n" + "="*60)
        print("OUTLIER DETECTION")
        print("="*60)
        
        outlier_summary = {}
        
        for col in columns:
            if col not in self.df.columns or self.df[col].isnull().all():
                continue
                
            data = self.df[col].dropna()
            
            if method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers = ((data < lower_bound) | (data > upper_bound)).sum()
            else:  # zscore
                z_scores = np.abs((data - data.mean()) / data.std())
                outliers = (z_scores > threshold).sum()
            
            if outliers > 0:
                outlier_summary[col] = outliers
                print(f"{col}: {outliers} outliers ({outliers/len(data)*100:.1f}%)")
        
        # Store the outlier summary as an attribute instead of returning it
        self.outlier_summary = outlier_summary
        
        # Return self to maintain method chaining
        return self
    
    def create_derived_features(self):
        """
        Create new features for analysis:
        - Quarter from month
        - Year-Month combination
        - Days since start
        - Price volatility indicators
        """
        print("\n" + "="*60)
        print("FEATURE ENGINEERING")
        print("="*60)
        
        # Create quarter
        self.df['quarter'] = self.df['month'].apply(lambda x: (x-1)//3 + 1 if pd.notna(x) else np.nan)
        print("✓ Created quarter feature")
        
        # Create year-month string
        self.df['year_month'] = self.df['year'].astype(str) + '-' + self.df['month'].astype(str).str.zfill(2)
        print("✓ Created year_month feature")
        
        # Calculate days since first date (for trend analysis)
        min_date = self.df['DATES'].min()
        self.df['days_since_start'] = (self.df['DATES'] - min_date).dt.days
        print("✓ Created days_since_start feature")
        
        return self
    
    def save_processed_data(self, output_path=None):
        """
        Save the processed dataset to a new CSV file.
        
        Args:
            output_path: Path for output file (default: adds '_processed' to input filename)
        """
        if output_path is None:
            input_path = Path(self.filepath)
            output_path = input_path.parent / f"{input_path.stem}_processed{input_path.suffix}"
        
        self.df.to_csv(output_path, index=False)
        print(f"\n✓ Processed data saved to: {output_path}")
        
        return self

if __name__ == "__main__":
    preprocessor = FoodPriceDataPreprocessor('real-time-food-prices-for-philippines.csv')
    
    # run preprocessing pipeline
    preprocessor.load_csv() \
                .explore_basic_info() \
                .identify_column_groups() \
                .convert_data_types() \
                .handle_missing_values(strategy='analyze') \
                .detect_outliers() \
                .create_derived_features() \
                .save_processed_data()
    
    # processed dataframe
    df_processed = preprocessor.df