import pandas as pd
import numpy as np
from pathlib import Path

class PovertyIncidenceProcessor:
    """
    A class to handle pre-analysis and pre-processing of poverty incidence data.
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
    
    def reshape(self):
        """
        Reshape data from wide to long format.
        Extract years from column names and create a 'year' column.
        """
        print("\n" + "="*60)
        print("RESHAPING DATA")
        print("="*60)
        
        # identify columns that contain year information
        year_columns = [col for col in self.df.columns if 
                        '(2018)' in col or 
                        '(2021)' in col or 
                        '(2023)' in col
                        ]
        id_columns = ['Region', 'Province']
        
        print(f"\nColumns with year data: {len(year_columns)}")
        print(f"ID columns: {id_columns}")
        
        # extract year suffix from columns and add new year "column"
        reshaped_data = []
        for year in [2018, 2021, 2023]:
            year_cols = [col for col in year_columns if f'({year})' in col]
            
            subset = self.df[id_columns + year_cols].copy()
            subset['year'] = year
            print(year, subset)
            
            # rename columns to remove year suffix
            rename_dict = {}
            for col in year_cols:
                new_name = col.replace(f' ({year})', '')
                rename_dict[col] = new_name
            
            subset.rename(columns=rename_dict, inplace=True)
            reshaped_data.append(subset)
        
        self.df_processed = pd.concat(reshaped_data, ignore_index=True)
        
        print(f"\n✓ Data reshaped from {self.nrows} rows to {len(self.df_processed)} rows")
        print(f"✓ Columns reduced from {self.ncols} to {len(self.df_processed.columns)}")
        print(f"\nNew columns: {self.df_processed.columns.tolist()}")
        
        return self
    
    def explore_data(self):
        """Display summary statistics and data overview."""
        print("\n" + "="*60)
        print("DATA OVERVIEW")
        print("="*60)
        
        print(f"\nShape: {self.df_processed.shape}")
        print(f"Years: {sorted(self.df_processed['year'].unique().tolist())}")
        print(f"Regions: {self.df_processed['Region'].nunique()}")
        print(f"Provinces: {self.df_processed['Province'].nunique()}")
        
        # Show sample data
        print("\nSample data:")
        print(self.df_processed.head(10).to_string(index=False))
        
        # Summary statistics
        print("\n" + "-"*60)
        print("SUMMARY STATISTICS")
        print("-"*60)
        print(self.df_processed.describe())
        
        return self
    
    def save_csv(self):
        input_path = Path(self.filepath)
        output_path = input_path.parent.parent / "processed-data" / f"{input_path.stem}_processed{input_path.suffix}"
        
        self.df_processed.to_csv(output_path, index=False)
        print(f"\n✓ Data processed: {self.df_processed.shape[0]} rows, {self.df_processed.shape[1]} columns") 
        print(f"✓ Data saved to: {output_path}")
        
        return self


if __name__ == "__main__":
    processor = PovertyIncidenceProcessor('raw-data/poverty-incidence.csv')
    
    # Run processing pipeline
    processor.load_csv() \
             .reshape()
            #  .explore() \
            #  .save_csv()
    
    # Access processed dataframe
    df_processed = processor.df_processed

