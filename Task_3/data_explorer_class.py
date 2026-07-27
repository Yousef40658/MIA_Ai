import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


class DataExplorer() :

    def __init__(self, df :pd.DataFrame):
        self.df = df

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
            
    def get_correlations(self, top_n=15):

        if self.numerical_df.empty:
            print("\nNo numerical columns found. Correlation analysis skipped.")
            return

        correlation_matrix = self.numerical_df.corr().round(2)

        corr_magnitude = self.numerical_df.corr().abs()
        np.fill_diagonal(corr_magnitude.values.copy(), 0)  # safe version

        scores = corr_magnitude.sum().sort_values(ascending=False)

        print("\n=== Feature Correlation Strength ===")
        print(scores)

        # Keep only the top_n most strongly-correlated features
        top_features = scores.head(top_n).index
        top_corr_matrix = correlation_matrix.loc[top_features, top_features]

        plt.figure(figsize=(8, 6))
        sns.heatmap(top_corr_matrix, annot=True, cmap='coolwarm')
        plt.title(f'Correlated Features')
        plt.show()

    def get_duplicates(self) :
        duplicates_count = self.df.duplicated().sum()
        print ("number of duplicates")
        print (duplicates_count)

    def target_correlation(self, target_col = "player_rating", top_n=10):
        corr = self.numerical_df.corr()[target_col].drop(target_col).sort_values(key=abs, ascending=False)
        print(f"\nCorrelation with {target_col}")
        print(corr)
        print(f"rows: {len(self.df)}")
        return corr

    def id_repeat_check(self):
        if "player_id" not in self.df.columns:
            return

        counts = self.df["player_id"].value_counts()

        print(f"Unique player_id: {counts.shape[0]} / Total rows: {len(self.df)}")
        print(f"Max repeats for a single player_id: {counts.max()}")

    def check_stat_consistency(self):
        issues = {}
        checks = [
            ('shots_on_target', 'shots', 'shots_on_target > shots'),
            ('successful_passes', 'total_passes', 'successful_passes > total_passes'),
            ('successful_dribbles', 'dribbles_attempted', 'successful_dribbles > dribbles_attempted'),
            ('successful_crosses', 'crosses', 'successful_crosses > crosses'),
        ]
        for num_col, denom_col, label in checks:
            if num_col in self.df.columns and denom_col in self.df.columns:
                bad = (self.df[num_col] > self.df[denom_col]).sum()
                issues[label] = bad
                print(f"{label}: {bad} rows")


    def exploration(self):
        self.basic_structure()
        self.values_inspection()
        self.check_for_skewness()
        self.check_outliers()
        self.get_duplicates()
        self.id_repeat_check()
        self.get_correlations()
        self.target_correlation()
        self.check_stat_consistency()

