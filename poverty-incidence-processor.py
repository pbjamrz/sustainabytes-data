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
        
        # identify year columns (columns w/ year suffix)
        year_columns = [col for col in self.df.columns if 
                        '(2018)' in col or 
                        '(2021)' in col or 
                        '(2023)' in col
                        ]
        id_columns = ['Region', 'Province']
        
        print(f"\nColumns with year data: {len(year_columns)}")
        print(f"ID columns: {id_columns}")
        
        # extract year suffix from columns and add new "year" column
        reshaped_data = []
        for year in [2018, 2021, 2023]:
            year_cols = [col for col in year_columns if f'({year})' in col]
            
            subset = self.df[id_columns + year_cols].copy()
            subset['Year'] = year
            
            # rename columns to remove year suffix
            rename_dict = {}
            for col in year_cols:
                new_name = col.replace(f' ({year})', '')
                rename_dict[col] = new_name
            
            subset.rename(columns=rename_dict, inplace=True)
            reshaped_data.append(subset)
        
        self.df_processed = pd.concat(reshaped_data, ignore_index=True)
        self.df_processed = self.df_processed[['Region', 'Province', 'Year',	
                                              'Annual Per Capita Poverty Threshold',
                                              'Poverty Incidence Among Families (%)',
                                              'Magnitude of Poor Families (1000)']]
        
        print(f"\n✓ Data reshaped from {self.nrows} rows to {len(self.df_processed)} rows")
        print(f"✓ Columns reduced from {self.ncols} to {len(self.df_processed.columns)}")
        print(f"\nNew columns: {self.df_processed.columns.tolist()}")
        
        return self
    
    def clean(self):
        """
        Clean data:
        - remove commas
        - convert data types
        - handle missing values
        """
        print("\n" + "="*60)
        print("CLEANING DATA")
        print("="*60)
        
        numeric_cols = [col for col in self.df_processed.columns
                        if col not in ['Region', 'Province'] 
                        ]
        
        # for each value, remove comma and convert to numeric data type
        for col in numeric_cols:
            self.df_processed[col] = self.df_processed[col].astype(str).str.replace(',', '')
            self.df_processed[col] = pd.to_numeric(self.df_processed[col], errors='coerce')
            
        print("✓ Removed commas from numeric values")
        print("✓ Converted to appropriate data types")
        
        # convert year to int
        self.df_processed['Year'] = self.df_processed['Year'].astype(int)
        
        return self
    
    def explore(self):
        """Display summary statistics and data overview."""
        print("\n" + "="*60)
        print("DATA OVERVIEW")
        print("="*60)
        
        print(f"\nShape: {self.df_processed.shape}")
        print(f"Years: {sorted(self.df_processed['Year'].unique().tolist())}")
        print(f"Regions: {self.df_processed['Region'].nunique()}")
        print(f"Provinces: {self.df_processed['Province'].nunique()}")
        
        # summary statistics
        print("\n" + "-"*60)
        print("SUMMARY STATISTICS")
        print("-"*60)
        print(self.df_processed.describe())
        
        # Check for missing values
        print(f"\nMissing values:")
        missing = self.df_processed.isnull().sum()
        missing = missing[missing > 0]
        for col, count in missing.items():
            pct = (count / len(self.df_processed)) * 100
            print(f"  - {col}: {count} ({pct:.1f}%)")
        
        return self
    
    def interpolate(self):
        """Interpolate data for missing years (2018-2023) and extrapolate for 2015-2017, 2024-2025."""
        print("\n" + "="*60)
        print("DATA INTERPOLATION & EXTRAPOLATION")
        print("="*60)
        
        # create complete year range for each province (2015-2025)
        provinces = self.df_processed[['Region', 'Province']].drop_duplicates()
        years = range(2015, 2026)  # 2015-2025
    
        complete_index = []
        for _, row in provinces.iterrows():
            for year in years:
                complete_index.append({
                    'Region': row['Region'],
                    'Province': row['Province'],
                    'Year': year
                })
        
        complete_df = pd.DataFrame(complete_index)
        
        # merge with existing data
        self.df_processed = complete_df.merge(
            self.df_processed,
            on=['Region', 'Province', 'Year'],
            how='left'
        )
        
        # interpolate & extrapolate numeric columns for each province
        self.df_processed = self.df_processed.sort_values(['Province', 'Year']).reset_index(drop=True)
        
        numeric_cols = ['Annual Per Capita Poverty Threshold',
                       'Poverty Incidence Among Families (%)',
                       'Magnitude of Poor Families (1000)']
        
        for col in numeric_cols:
            # first interpolate between known points (2018-2023)
            self.df_processed[col] = self.df_processed.groupby('Province')[col].transform(
                lambda x: x.interpolate(method='linear', limit_direction='both')
            )
            
            # then extrapolate linearly for 2015-2017 and 2024-2025
            self.df_processed[col] = self.df_processed.groupby('Province')[col].transform(
                lambda x: x.interpolate(method='linear', limit_direction='both', fill_value='extrapolate')
            )
        
        print(f"✓ Interpolated data for years 2018-2023")
        print(f"✓ Extrapolated data for years 2015-2017 and 2024-2025")
        print(f"✓ New shape: {self.df_processed.shape}")
        
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
             .reshape() \
             .clean() \
             .explore() \
             .interpolate() \
             .save_csv()
    
    # Access processed dataframe
    df_processed = processor.df_processed

