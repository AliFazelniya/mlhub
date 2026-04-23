import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

class Preprocessor:
    def __init__(self, df):
        self.df = df.copy()

    def drop_id(self):
        if 'CustomerID' in self.df.columns:
            self.df = self.df.drop(columns=['CustomerID'])

    def encode_gender(self):
        if 'Gender' in self.df.columns:
            self.df['Gender'] = (self.df['Gender'] == 'Female').astype(int)

    def select_and_scale(self):
        features = ['Annual Income (k$)', 'Spending Score (1-100)']
        X = self.df[features].values.astype(float)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.df = pd.DataFrame(X_scaled, columns=features)

    def transform(self):
        self.drop_id()
        self.encode_gender()
        self.select_and_scale()
        return self.df