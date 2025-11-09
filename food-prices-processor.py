import pandas as pd
import numpy as np
from pathlib import Path

class FoodPricesProcessor:
    """
    A class to handle prea-analysis and pre-processing of the food price dataset.
    """
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        
    def load_csv(self):
        self.df = pd.read_csv(self.filepath)
        self.nrows = self.df.shape[0]
        self.ncols = self.df.shape[1]
        
        print(f"Dataset loaded: {self.nrows} rows, {self.ncols} columns")
        return self
    
    def explore_basic_info(self):
        """
        Display basic information about the dataset:
        - Geographic coverage
        - Date range coverage
        - Missing value statistics
        """
        
        print("\n" + "="*60)
        print("DATASET OVERVIEW")
        print("="*60)
        
        # geographic coverage
        print(f"\nGeographic Coverage:")
        print(f"  - Countries: {self.df['country'].nunique()}")
        print(f"  - Regions: {self.df['adm1_name'].nunique()}")
        print(f"  - Provinces: {self.df['adm2_name'].nunique()}")
        print(f"  - Markets: {self.df['mkt_name'].nunique()}") # can be cities, barangays, muncipalities inside the province
        
        # date range
        print(f"\nTemporal Coverage:")
        print(f"  - Years: {sorted(self.df['year'].unique())}")
        print(f"  - Date range: {self.df['DATES'].min()} to {self.df['DATES'].max()}")
        
        # junk columns — food columns w/ a lot of missing values
        print(f"\nJunk Columns:")
        self.missing_entries = self.df.isnull() # returns dataframe of same shape where each cell is True if original cell is empty
        
        nmissing_entries = self.missing_entries.sum() / self.nrows * 100
        nmissing_entries = nmissing_entries.sort_values(ascending=False)
        
        print(f"  - Columns with >50% missing: {(nmissing_entries > 50).sum()}")
        print(f"  - Columns with >90% missing: {(nmissing_entries > 90).sum()}")
        
        return self
    
    def identify_column_groups(self):
        """
        Categorize columns into groups for easier processing:
        - Geographic identifiers
        - Temporal identifiers
        - Metadata 
        - Price columns
        - Derived metrics
        """
        cols = self.df.columns.tolist()
        
        # geographic identifiers
        self.geo_cols = ['ISO3', 'country', 'adm1_name', 'adm2_name', 
                         'mkt_name', 'lat', 'lon', 'geo_id']
        
        # temporal identifiers
        self.time_cols = ['DATES', 'year', 'month']
        
        # metadata and quality indicators
        self.meta_cols = ['currency', 'components', 'start_dense_data', 
                          'last_survey_point', 'data_coverage', 
                          'data_coverage_recent', 'index_confidence_score', 
                          'spatially_interpolated']
        
        # base food item price columns (no prefix)
        self.food_cols = [col for col in cols 
                          if not any(col.startswith(prefix) for prefix in 
                                   ['o_', 'h_', 'l_', 'c_', 'inflation_', 'trust_'])
                          and col not in self.geo_cols + self.time_cols + self.meta_cols]
        
        # derived metric index columns
        # o_ = opening price, h_ = high, l_ = low, c_ = closing
        self.derived_index_cols = {
            'open': [col for col in cols if col.startswith('o_') and col.endswith('_index')],
            'high': [col for col in cols if col.startswith('h_') and col.endswith('_index')],
            'low': [col for col in cols if col.startswith('l_') and col.endswith('_index')],
            'close': [col for col in cols if col.startswith('c_') and col.endswith('_index')],
            'inflation': [col for col in cols if col.startswith('inflation_') and col.endswith('_index')],
            'trust': [col for col in cols if col.startswith('trust_') and col.endswith('_index')]
        }
        
        # derived metric columns with prefixes
        self.derived_cols = {
            'open': [col for col in cols if col.startswith('o_') and not col.endswith('_index')],
            'high': [col for col in cols if col.startswith('h_') and not col.endswith('_index')],
            'low': [col for col in cols if col.startswith('l_') and not col.endswith('_index')],
            'close': [col for col in cols if col.startswith('c_') and not col.endswith('_index')],
            'inflation': [col for col in cols if col.startswith('inflation_') and not col.endswith('_index')],
            'trust': [col for col in cols if col.startswith('trust_') and not col.endswith('_index')]
        }
        
        print(f"{self.food_cols}")
        print(f"{self.derived_cols}")
        
        print("\n" + "="*60)
        print("COLUMN GROUPS")
        print("="*60)
        print(f"Geographic: {len(self.geo_cols)} columns")
        print(f"Temporal: {len(self.time_cols)} columns")
        print(f"Metadata: {len(self.meta_cols)} columns")
        print(f"Base food items: {len(self.food_cols)} columns")
        print(f"Derived metric index: {len(self.derived_index_cols)} columns")
        print(f"Derived metrics:")
        for key, cols in self.derived_cols.items():
            print(f"  - {key}: {len(cols)} columns")
        
        return self
    
    def handle_missing_values(self):
        pass

    def convert_data_types(self):
        pass
    
    def detect_outliers(self, columns=None, method='iqr', threshold=3):
        pass
    
    def save_csv(self):
        input_path = Path(self.filepath)
        output_path = input_path.parent.parent / "processed-data" / f"{input_path.stem}_processed{input_path.suffix}"
        
        self.df.to_csv(output_path, index=False)
        print(f"\nProcessed data saved to: {output_path}")
        
        return self

if __name__ == "__main__":
    preprocessor = FoodPricesProcessor('raw-data/food-prices.csv')
    
    # run preprocessing pipeline
    preprocessor.load_csv() \
                .explore_basic_info() \
                .identify_column_groups() \
                .save_csv()
    
    # processed dataframe
    df_processed = preprocessor.df