import matplotlib.pyplot as plt
import pandas as pd

# 1. Marktaktivität (Verkäufe, Angebot, Nachfrage)
def plot_market_activity(results):
    plt.figure(figsize=(12, 6))
    plt.plot(results["Verkäufe"], label="Kumulative Verkäufe", linewidth=2)
    plt.plot(results["Angebot"], label="Angebot (aktive Listings)", linestyle="--")
    plt.plot(results["Nachfrage"], label="Nachfrage (aktive Käufer:innen)", linestyle="--")
    plt.xlabel("Kalenderwochen")
    plt.ylabel("Anzahl")
    plt.title("Marktaktivität: Verkäufe, Angebot, Nachfrage")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 2. Zinsentwicklung
def plot_interest_rate(results):
    plt.figure(figsize=(10, 5))
    plt.plot(results["Zinsniveau"], label="Hypothekarzins (%)", color="green")
    plt.xlabel("Kalenderwochen")
    plt.ylabel("Zinssatz (%)")
    plt.title("Zinsentwicklung über die Zeit")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# 3. Käufer:innen Budgets
def plot_buyer_budgets(buyer_budgets):
    plt.figure(figsize=(10, 5))
    plt.hist(buyer_budgets, bins=20, color="skyblue", edgecolor="black")
    plt.xlabel("Budget der Käufer:innen (CHF)")
    plt.ylabel("Anzahl Käufer:innen")
    plt.title("Verteilung der Käuferbudgets")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 4. Käufer:innen Wohnlage
def plot_buyer_locations(buyer_locations):
    counts = pd.Series(buyer_locations).value_counts()
    plt.figure(figsize=(12, 6))
    counts.plot(kind="bar", color="lightcoral", edgecolor="black")
    plt.xlabel("Quartier")
    plt.ylabel("Anzahl Käufer:innen")
    plt.title("Wohnpräferenzen der Käufer:innen")
    plt.xticks(rotation=45)
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.show()

# 5. Verkaufspreise Verkäufer:innen
def plot_seller_prices(seller_prices):
    plt.figure(figsize=(10, 5))
    plt.hist(seller_prices, bins=20, color="gold", edgecolor="black")
    plt.xlabel("Verkaufspreise der Immobilien (CHF)")
    plt.ylabel("Anzahl Immobilien")
    plt.title("Verteilung der Verkaufspreise")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 6. Verkäufer:innen Wohnlage
def plot_seller_locations(seller_locations):
    counts = pd.Series(seller_locations).value_counts()
    plt.figure(figsize=(12, 6))
    counts.plot(kind="bar", color="mediumseagreen", edgecolor="black")
    plt.xlabel("Quartier")
    plt.ylabel("Anzahl aktiver Listings")
    plt.title("Standorte der aktiven Verkäufer:innen")
    plt.xticks(rotation=45)
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.show()
