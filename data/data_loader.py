import pandas as pd

def load_population_data():
    return pd.read_csv("data/Cleaned/bevoelkerungZuerichCleaned.csv")

def load_income_data():
    return pd.read_csv("data/Cleaned/einkommenZuerichCleaned.csv")

def load_building_data():
    return pd.read_csv("data/Cleaned/gebauedeZuerich2024Cleaned.csv")

def load_trends_data():
    buyer_df = pd.read_csv("data/Cleaned/google_trends_buyer.csv")
    trend_columns = ["Immobilie kaufen Zürich", "Haus kaufen Zürich", "Wohnung kaufen Zürich", "Immobilien Kaufpreise"]
    buyer_trend = buyer_df[trend_columns].mean(axis=1).fillna(0).tolist()

    # Luxuskonsumtrends synthetisch
    import numpy as np
    weeks = np.arange(52)
    luxury_trend = (
        0.3 + 0.2 * np.sin(2 * np.pi * weeks / 52) + 0.1 * np.random.normal(0, 0.3, size=52)
    )
    luxury_trend = np.clip(luxury_trend, 0, 1).tolist()
    return buyer_trend, luxury_trend
