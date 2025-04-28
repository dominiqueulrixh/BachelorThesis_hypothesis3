from agents.buyer_agent import BuyerAgent
from agents.seller_agent import SellerAgent

from model.housing_market_model import HousingMarketModel
from analysis.market_analysis import get_market_state_by_kreis, plot_market_state, generate_early_warnings
from analysis.matching_analysis import create_matching_dataframe

import matplotlib.pyplot as plt
import pandas as pd

# Modell starten
model = HousingMarketModel(
    n_buyers=20,
    n_sellers=5,
    n_potential_sellers=10
)

# Simulation laufen lassen
for _ in range(52):  # 52 Wochen
    model.step()

# Ergebnisse abrufen
results = model.datacollector.get_model_vars_dataframe()


# Diagramm 1: Marktspannung
marktspannung = results["Nachfrage"] / results["Angebot"]

plt.figure(figsize=(12, 6))
plt.plot(marktspannung, marker='o', linestyle='-', color='purple')
plt.axhline(1, color='grey', linestyle='--', label="Gleichgewicht Käufer/Verkäufer")
plt.xlabel("Kalenderwoche")
plt.ylabel("Nachfrage / Angebot Verhältnis")
plt.title("📈 Marktspannung: Käufer- zu Verkäuferverhältnis")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# Diagramm 2: Dynamik der Marktakteure
plt.figure(figsize=(14, 7))
plt.stackplot(
    results.index,
    results["Nachfrage"],
    results["Angebot"],
    results["Potenzielle Verkäufer"],
    labels=["Nachfrage", "Angebot", "Potenzielle Verkäufer"],
    colors=["orange", "green", "red"],
    alpha=0.7
)
plt.xlabel("Kalenderwoche")
plt.ylabel("Anzahl Akteure")
plt.title("📊 Dynamik der Marktakteure (Stacked Area Chart)")
plt.legend(loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()


# Diagramm 3: Käuferaktivierung vs. Zinsniveau
buyers_activation = results["Nachfrage"] / (results["Nachfrage"] + results["Potenzielle Verkäufer"])

plt.figure(figsize=(12, 6))
plt.plot(results.index, buyers_activation, label="Aktivierungsrate Käufer:innen", color="blue")
plt.plot(results.index, results["Zinsniveau"]/max(results["Zinsniveau"]), label="Normiertes Zinsniveau", linestyle="--", color="black")
plt.xlabel("Kalenderwoche")
plt.ylabel("Rate / Zinsniveau (normalisiert)")
plt.title("💡 Aktivierungsrate Käufer:innen vs. Zinsentwicklung")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Diagramm 4: Verkaufserfolg pro Woche
plt.figure(figsize=(12, 6))
plt.bar(results.index, results["Verkäufe"], color="teal")
plt.xlabel("Kalenderwoche")
plt.ylabel("Anzahl Verkäufe")
plt.title("🏠 Anzahl Verkäufe pro Woche")
plt.grid(axis='y')
plt.tight_layout()
plt.show()

# Käufer:innen Übersicht erstellen
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

# Verkäufer:innen Übersicht erstellen
sellers_data = []
for agent in model.schedule.agents:
    if isinstance(agent, SellerAgent):
        sellers_data.append({
            "Kreis (Immobilie)": agent.location,
            "Fläche (m²)": round(agent.area, 2),
            "Bauperiode": agent.build_year_category,
            "Preis (CHF)": round(agent.price),
            "Gelisted": agent.listed
        })

sellers_df = pd.DataFrame(sellers_data)

# Gelistete Listings zuerst anzeigen
sellers_df = sellers_df.sort_values(by="Gelisted", ascending=False).reset_index(drop=True)

print("\n🏠 Übersicht der Verkäufer:innen:")
print(sellers_df)

# Marktanalyse
markt_df = get_market_state_by_kreis(model)
early_warnings = generate_early_warnings(markt_df)

# Marktübersicht
plot_market_state(markt_df, model.current_week)

# Broker Kaufvorschläge abrufen
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

# Kaufvorschläge Übersicht
matches = model.broker.suggest_matches()
matching_df = create_matching_dataframe(matches)

print("\n📊 Übersicht der Kaufvorschläge (Matching-DataFrame):")
print(matching_df)

# Ergebnisse speichern
buyers_df.to_csv('data/buyers.csv', index=False)
sellers_df.to_csv('data/sellers.csv', index=False)
matching_df.to_csv('data/matchings.csv', index=False)

# Tests starten
# Modell starten
model = HousingMarketModel()
# Tests ausführen
model.test_agent.run_zins_test()

# Ergebnisse plotten
model.test_agent.plot_results()
# t-Test ausführen
model.test_agent.run_t_test()

# Behavioral Data Test starten
model.test_agent.run_behavioral_data_test()
# Ergebnisse plotten
model.test_agent.run_behavioral_t_test()

