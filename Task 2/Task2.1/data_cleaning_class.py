import pandas as pd
import numpy as np
from scipy.stats import zscore

class DataCleaner():
    def __init__(self , file_path): 
        pd.set_option('display.max_columns', None)
        self.df = pd.read_csv(file_path , low_memory= False)

        #extract numerical cols
        self.numerical_df = self.df.select_dtypes(include='number')

    def drop_duplicates(self):
        self.df = self.df.drop_duplicates()

    def clean_col_names(self): 
        original = self.df.columns.tolist()
        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(' ', '_')
            .str.replace(r'[^\w]', '', regex=True)
        )

    def handle_missing(self, col_threshold=0.3, row_threshold=0.3):
        #drop columns with too many nulls
        null_percent = self.df.isnull().mean()
        cols_to_drop = null_percent[null_percent > col_threshold].index
        self.df = self.df.drop(columns=cols_to_drop)

        #refreshing since cols changed
        self.numerical_df = self.df.select_dtypes(include='number')
        text_cols = self.df.select_dtypes(include='object').columns

        # drop rows missing a text value since they can't be replaced 
        self.df = self.df.dropna(subset=text_cols)

        self.df = self.df[self.df.isnull().sum(axis=1) <= 3]

        # 4. fill any remaining numeric nulls with the column mean
        self.numerical_df = self.df.select_dtypes(include='number')
        for col in self.numerical_df.columns:
            self.df[col] = self.df[col].fillna(self.df[col].mean())

        self.numerical_df = self.df.select_dtypes(include='number')

    def handle_outliers(self, z_threshold=3):
        z = np.abs(zscore(self.numerical_df, nan_policy="omit"))
        z_df = pd.DataFrame(z, columns=self.numerical_df.columns, index=self.numerical_df.index)

        rows_to_keep = (z_df <= z_threshold).all(axis=1)
        self.df = self.df.loc[rows_to_keep]

        self.numerical_df = self.df.select_dtypes(include='number')
