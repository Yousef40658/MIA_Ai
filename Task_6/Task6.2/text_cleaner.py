import pandas as pd

class TextCleaner():
    def __init__(self , str_series : pd.Series) :
        self.series = str_series
        self.lowercase()
        self.remove_punctuation()
        self.normalize_whitespace()
        self.filter_min_length()
        self.drop_empty_series()

        print ("Text cleaned")



    def lowercase(self):
        self.series = self.series.str.lower()

    def remove_punctuation(self):
        #keeping only letters , must be done after lowercase since i didn't include A-Z
        self.series = self.series.str.replace(r"[^a-z\s]", "", regex=True)

    def normalize_whitespace(self):
        self.series = self.series.str.strip().str.replace(r"\s+", " ", regex=True)

    def drop_empty_series(self):
        self.series = self.series[self.series.str.len() > 0]

    def clean_series(self):
        return self.series

    def filter_min_length(self, min_words=3):
        word_counts = self.series.str.split().str.len()
        self.series = self.series[word_counts >= min_words]


    
