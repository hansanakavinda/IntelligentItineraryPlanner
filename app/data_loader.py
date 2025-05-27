import pandas as pd

def load_data():
    data = pd.read_csv("data/attractions.csv")
    data.dropna(subset=["Latitude", "Longitude"], inplace=True)
    return data
