import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import zscore

class DataExplorer() :

    def __init__(self , file_path) :
        pd.set_option('display.max_columns', None)
        try :
            if file_path.endswith('.csv') :
                self.df = pd.read_csv(file_path ,low_memory= False)
                # print ("CSV file opened correctly")

            elif file_path.endswith('.xlsx') :
                 self.df = pd.read_excel(file_path , engine='openpyxl' , header= 1 )
                 print ("Excel file opened correctly")

            else :
                raise ValueError("Unsupported file format")
                
        except Exception as e :
            print(f"Error reading file:\n{e}")


        self.numerical_df = self.df.select_dtypes(include='number')
            

    def basic_structure(self) :
        print ("-----------------")
        print (f"DataSet Shape is {self.df.shape}")
        print ("-----------------")

        #
        # for col in self.df.columns:
        #     print(f"{col} ({self.df[col].dtype})")
        #     # print(self.df[col].head(3))
        #     # print("-" * 40)

        print ("-----------------\n\n")

    def values_inspection(self, check_null=True):
        print("=== STATISTICS ===")
        print(self.df.describe(percentiles=[.25, .5, .75, .99]))

        if check_null:
            print("\n=== NULL VALUES ===")
            null_counts = self.df.isnull().sum()
            null_percent = (null_counts / len(self.df)) * 100

            summary = self.df.dtypes.to_frame(name='dtype')
            summary['null_count'] = null_counts
            summary['null_%'] = null_percent

            print(summary)

        # Print boolean statistics if they exist
        boolean_cols = self.df.select_dtypes(include='bool')

        if not boolean_cols.empty:
            print("\n=== BOOLEAN COUNTS ===")
            for col in boolean_cols.columns:
                count = boolean_cols[col].sum()
                percent = boolean_cols[col].mean() * 100
                print(f"{col:<12}: {count} ({percent:.2f}%)")

    def check_for_skewness(self , histogram = False):
        print ("Skewness")
        print(self.numerical_df.skew())

        if histogram :
            self.df.hist(bins = 15)
            plt.show()

    def check_outliers(self):

        z = np.abs(zscore(self.numerical_df, nan_policy="omit"))
        z_df = pd.DataFrame(z, columns=self.numerical_df.columns)

        outliers = z_df > 3

        print("\n=== Number of outliers per column ===")
        print(outliers.sum())

        return (outliers.sum())
            
    def get_correlations(self) :

        if self.numerical_df.empty:
            print("\nNo numerical columns found. Correlation analysis skipped.")
            return
        
        correlation_matrix = self.numerical_df.corr().round(2)

        corr_magnitude = self.numerical_df.corr().abs()
        np.fill_diagonal(corr_magnitude.values.copy(), 0)  # safe version

        scores = corr_magnitude.sum().sort_values(ascending=False)

        print("\n=== Feature Correlation Strength ===")
        print(scores)


        plt.figure(figsize=(8,6))
        sns.heatmap(correlation_matrix , annot= True , cmap= 'coolwarm')
        plt.title('Correlations')
        plt.show()

        #

    
    def get_duplicates(self) :
        duplicates_count = self.df.duplicated().sum()
        print ("number of duplicates")
        print (duplicates_count)


 