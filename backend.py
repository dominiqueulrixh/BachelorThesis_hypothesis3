import pandas as pd

# Käufer laden
def load_buyers():
    buyers = pd.read_csv('data/buyers.csv')
    return buyers

# Verkäufer laden
def load_sellers():
    sellers = pd.read_csv('data/sellers.csv')
    return sellers

# Matching-Vorschläge laden (nur die über Schwellwert)
def get_matchings(threshold=70):
    matchings = pd.read_csv('data/matchings.csv')

    # Korrekte Spalte "MatchingScore" verwenden
    if "MatchingScore" in matchings.columns:
        score_col = "MatchingScore"
    else:
        raise ValueError("MatchingScore-Spalte fehlt in matchings.csv!")

    return matchings[matchings[score_col] >= threshold]