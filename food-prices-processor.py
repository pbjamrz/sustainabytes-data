import pandas as pd
import numpy as np
from pathlib import Path

class FoodPricesProcessor:
    """
    A class to handle pre-analysis and pre-processing of the food price dataset.
    """
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.df_processed = None
        
    def load_csv(self):
        self.df = pd.read_csv(self.filepath)
        self.nrows = self.df.shape[0]
        self.ncols = self.df.shape[1]
        
        print(f"✓ Dataset loaded: {self.nrows} rows, {self.ncols} columns")
        return self
    
    def explore(self):
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
        print(f"  - Years: {sorted(self.df['year'].unique().tolist())}")
        print(f"  - Date range: {self.df['DATES'].min()} to {self.df['DATES'].max()}")
        
        # junk columns — food columns w/ a lot of missing values
        print(f"\nJunk Columns:")
        missing_entries = self.df.isnull() # returns dataframe of same shape where each cell is True if original cell is empty
        
        nmissing_entries = missing_entries.sum() / self.nrows * 100
        nmissing_entries = nmissing_entries.sort_values(ascending=False)
        
        print(f"  - Columns with >50% missing: {(nmissing_entries > 50).sum()}")
        print(f"  - Columns with >90% missing: {(nmissing_entries > 90).sum()}")
        
        return self
    
    def categorize_cols(self):
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
        
        # base food item price columns (w/o prefixes)
        self.food_cols = [col for col in cols 
                          if not any(col.startswith(prefix) for prefix in 
                                   ['o_', 'h_', 'l_', 'c_', 'inflation_', 'trust_'])
                          and col not in self.geo_cols + self.time_cols + self.meta_cols]
        
        # derived metric columns (w/ prefixes)
        # o_ = opening price, h_ = high, l_ = low, c_ = closing
        self.derived_cols = {
            'open': [col for col in cols if col.startswith('o_') and not col.endswith('_index')],
            'high': [col for col in cols if col.startswith('h_') and not col.endswith('_index')],
            'low': [col for col in cols if col.startswith('l_') and not col.endswith('_index')],
            'close': [col for col in cols if col.startswith('c_') and not col.endswith('_index')],
            'inflation': [col for col in cols if col.startswith('inflation_') and not col.endswith('_index')],
            'trust': [col for col in cols if col.startswith('trust_') and not col.endswith('_index')]
        }
        
        # derived metric index columns 
        self.derived_index_cols = [col for col in cols 
                                   if any(col.startswith(prefix) for prefix in 
                                          ['o_', 'h_', 'l_', 'c_', 'inflation_', 'trust_']) 
                                   and col.endswith('_index')]
        
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
    
    def simplify(self):
        """
        Simplify dataset by keeping only the relevant columns:
        - year
        - region (adm2_name)
        - closing food prices
        Then remove columns with >50% missing entries
        """
        print("\n" + "="*60)
        print("SIMPLIFY DATASET")
        print("="*60)
        
        # keep relevant columns
        print("\nKeep relevant columns:")
        cols_to_keep = ['year', 'adm2_name'] + self.derived_cols['close']
        self.df_processed = self.df[cols_to_keep].copy()
        print(f"✓ Removed {self.ncols - len(cols_to_keep)} unnecessary columns")
        
        # remove junk columns
        print("\nRemove junk columns:")
        missing_entries = self.df_processed.isnull() # returns dataframe of same shape where each cell is True if original cell is empty
        nmissing_entries = missing_entries.sum() / self.df_processed.shape[0] * 100 # returns series (list) where index -> column, value -> percentage
    
        print(f"  - Columns with >50% missing: {(nmissing_entries > 50).sum()}")
        print(f"  - Columns with >90% missing: {(nmissing_entries > 90).sum()}")
        print(f"  - Columns with 100% missing: {(nmissing_entries == 100).sum()}")
        
        m = nmissing_entries.gt(90.0)
        cols_to_rmv = self.df_processed.loc[:,m].columns.tolist()   
        self.df_processed.drop(cols_to_rmv, axis=1, inplace=True)
        print(f"✓ Removed {len(cols_to_rmv)} junk columns")
        print(f"✓ Missing values: {self.df_processed.isnull().sum().sum()} cells")
        
        print("\nKeep columns:")
        for col in self.df_processed.columns:
            print(f"  - {col}")
        
        print("\nRemove rows outside of 2015-2025:")
        series_to_rmv =  ~(2015 <= self.df_processed['year']) & (self.df_processed['year'] <= 2025)
        self.df_processed.drop(self.df_processed[series_to_rmv].index, inplace = True)
        print(f"✓ Removed {len(series_to_rmv)}")
        
        return self

    def aggregate_prices(self):
        """
        Goup rows by region and year. Then, find mean price of each food item
        """

        print("\n" + "="*60)
        print("AGGREGATE DATASET")
        print("="*60)

        print("\nGroup rows by region and year:")
        self.df_processed = self.df_processed.groupby(['year', 'adm2_name']).mean()
        print(self.df_processed)
        self.df_processed.reset_index(inplace=True)
        
        return self

    def clean(self):
        pass
    
    def save_csv(self):
        input_path = Path(self.filepath)
        output_path = input_path.parent.parent / "processed-data" / f"{input_path.stem}_processed{input_path.suffix}"
        
        self.df_processed.to_csv(output_path, index=False)
        print(f"\n✓ Data processed: {self.df_processed.shape[0]} rows, {self.df_processed.shape[1]} columns") 
        print(f"✓ Data saved to: {output_path}")
        
        return self

if __name__ == "__main__":
    preprocessor = FoodPricesProcessor('raw-data/food-prices.csv')
    
    # run preprocessing pipeline
    preprocessor.load_csv() \
                .explore() \
                .categorize_cols() \
                .simplify() \
                .aggregate_prices() \
                .save_csv()
    
    # processed dataframe
    df_processed = preprocessor.df_processed