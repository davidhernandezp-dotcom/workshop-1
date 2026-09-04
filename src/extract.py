import pandas as pd


def extract(path='data/raw/candidates.csv'):
   
    df = pd.read_csv(path, sep=';')
    return df