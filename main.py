from agents.buyer_agent import BuyerAgent
from agents.seller_agent import SellerAgent
from agents.potentialSeller_agent import PotentialSellerAgent

from model.housing_market_model import HousingMarketModel
from analysis.market_analysis import get_market_state_by_kreis, plot_market_state, generate_early_warnings
from analysis.matching_analysis import create_matching_dataframe

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Hilfsfunktion: Fläche leicht variieren
def jitter_area(area):
    if area <= 50:
        jitter = np.random.uniform(-5, 5)  # Kleine Gebäude kleinere Schwankung
    elif area <= 150:
        jitter = np.random.uniform(-7, 7)  # Mittlere Gebäude
    else:
        jitter = np.random.uniform(-10, 10)  # Große Gebäude

    return max(10, area + jitter)  # Nie kleiner als 10 m²!

# --- Modell starten ---
model = HousingMarketModel(
    n_buyers=20,
    n_sellers=5,
    n_potential_sellers=10
)

# --- Simulation laufen lassen ---
for _ in range(52):  # 52 Wochen
    model.step()

# --- Ergebnisse abrufen ---
results = model.datacollector.get_model_vars_dataframe()

# --- Ergebnisse visualisieren ---
plt.figure(figsize=(12, 6))
plt.plot(results["Verkäufe"], label="Kumulative Verkäufe")
plt.plot(results["Angebot"], label="Angebot (aktive Listings)")
plt.plot(results["Nachfrage"], label="Nachfrage (aktive Käufer:innen)")
plt.plot(results["Zinsniveau"], label="Zinsniveau (BankAgent)", linestyle="--")
plt.xlabel("Kalenderwoche")
plt.ylabel("Anzahl / Prozent")
plt.title("Immobilienmarktaktivität (Prototyp Hypothese 3)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Käufer:innen Übersicht ---
buyers_data = []
for agent in model.schedule.agents:
    if isinstance(agent, BuyerAgent):
        buyers_data.append({
            "BuyerID": agent.unique_id,
            "Alter": agent.profile.age,
            "Kreis (Wohnort)": agent.location,
            "Budget (CHF)": round(agent.budget),
            "Einkommen (CHF)": round(agent.profile.income * 1000),
        })

buyers_df = pd.DataFrame(buyers_data)
print("\n🧍 Übersicht der Käufer:innen:")
print(buyers_df)

# --- Verkäufer:innen Übersicht ---
sellers_data = []
for agent in model.schedule.agents:
    if isinstance(agent, SellerAgent):
        # Fläche jittern
        original_area = agent.area
        adjusted_area = jitter_area(original_area)

        # Preis proportional anpassen
        price_per_m2 = agent.price / original_area if original_area > 0 else 10000  # fallback
        adjusted_price = adjusted_area * price_per_m2

        sellers_data.append({
            "Kreis (Immobilie)": agent.location,
            "Fläche (m²)": round(adjusted_area, 2),
            "Bauperiode": agent.build_year_category,
            "Preis (CHF)": round(adjusted_price),
            "Gelisted": agent.listed
        })

sellers_df = pd.DataFrame(sellers_data)

# --- Verkäufer:innen sortieren: Gelistete zuerst ---
sellers_df = sellers_df.sort_values(by="Gelisted", ascending=False).reset_index(drop=True)

print("\n🏠 Übersicht der Verkäufer:innen:")
print(sellers_df)

# --- Marktanalyse durchführen ---
markt_df = get_market_state_by_kreis(model)
early_warnings = generate_early_warnings(markt_df)

# --- Marktübersicht plotten ---
plot_market_state(markt_df, model.current_week)

# --- Broker Kaufvorschläge abrufen ---
suggestions = model.broker.suggest_matches()

print("\n🤝 Kaufvorschläge durch Broker:")
if suggestions:
    for suggestion in suggestions:
        verkaufsweg = "über Broker" if suggestion['ViaBroker'] else "Peer-to-Peer"
        print(
            f"Käufer #{suggestion['BuyerID']} (Budget: {suggestion['BuyerBudget']:,} CHF, Kreis {suggestion['BuyerKreis']}) "
            f"könnte Immobilie #{suggestion['SellerID']} (Preis: {suggestion['OfferPrice']:,} CHF, "
            f"Kreis {suggestion['SellerKreis']}) kaufen.\n"
            f"➔ Matching-Score: {suggestion['MatchingScore']}%\n"
            f"➔ Finaler Kaufpreis ({verkaufsweg}): {suggestion['FinalPrice']:,} CHF\n"
            f"➔ Gründe: {', '.join(suggestion['Comments'])}\n"
        )
else:
    print("Keine passenden Kaufvorschläge gefunden.")

# --- Matching Übersicht ---
matches = model.broker.suggest_matches()
matching_df = create_matching_dataframe(matches)

print("\n📊 Übersicht der Kaufvorschläge (Matching-DataFrame):")
print(matching_df)

# --- Ergebnisse speichern ---
buyers_df.to_csv('data/buyers.csv', index=False)
sellers_df.to_csv('data/sellers.csv', index=False)
matching_df.to_csv('data/matchings.csv', index=False)
