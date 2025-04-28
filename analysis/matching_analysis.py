import pandas as pd

def create_matching_dataframe(matches):
    # Erzeugt DataFrame der aktuellen Kaufvorschläge
    df = pd.DataFrame(matches)
    if not df.empty:
        df = df.sort_values(by="MatchingScore", ascending=False)
    return df
