# luxuskonsum_generator.py

import pandas as pd
import numpy as np

# --- Parameter ---
np.random.seed(42)
weeks = 52

# --- Grundsaisonale Kurve erstellen ---
# z.B. im Januar Loch, im Frühling und Herbst Peaks
base_curve = (
    50 + 20 * np.sin(np.linspace(0, 2 * np.pi, weeks)) +  # Jahres-Saison
    10 * np.sin(np.linspace(0, 8 * np.pi, weeks))          # Quartalsschwankungen
)

# --- Zufällige Abweichungen hinzufügen ---
noise = np.random.normal(0, 5, size=weeks)

luxury_index = np.clip(base_curve + noise, 0, 100)  # auf Bereich 0–100 begrenzen

# --- In DataFrame packen ---
luxury_df = pd.DataFrame({
    "Woche": range(1, weeks + 1),
    "LuxuskonsumIndex": luxury_index
})

# --- Speichern ---
luxury_df.to_csv("../data/Cleaned/luxuskonsum_trend.csv", index=False)

print("✅ Luxuskonsumdaten erfolgreich gespeichert: 'data/cleaned/luxuskonsum_trend.csv'")
