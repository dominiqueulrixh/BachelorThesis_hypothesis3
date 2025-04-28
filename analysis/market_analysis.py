import pandas as pd
import matplotlib.pyplot as plt

def get_market_state_by_kreis(model):
    # Aggregiert aktuellen Marktstatus nach KreisCd (Quartier)
    kreise = model.building_data['KreisCd'].unique()

    data = []
    for kreis in kreise:
        active_buyers = sum(
            1 for a in model.schedule.agents
            if hasattr(a, "location") and a.location == kreis and hasattr(a, "active") and a.active
        )
        active_sellers = sum(
            1 for a in model.schedule.agents
            if hasattr(a, "location") and a.location == kreis and hasattr(a, "listed") and a.listed
        )
        potential_sellers = sum(
            1 for a in model.schedule.agents
            if hasattr(a, "location") and a.location == kreis and hasattr(a, "ready_to_sell") and not a.ready_to_sell
        )

        potential_buyers = sum(
            1 for a in model.schedule.agents
            if hasattr(a, "location") and a.location == kreis and hasattr(a, "active") and not a.active
        )

        data.append({
        "Kreis": kreis,
        "Aktive Käufer:innen": active_buyers,
        "Potentielle Käufer:innen": potential_buyers,
        "Aktive Verkäufer:innen (Listings)": active_sellers,
        "Potentielle Verkäufer:innen": potential_sellers,
        })

    df = pd.DataFrame(data)
    df = df.sort_values("Kreis")
    return df

def plot_market_state(df, current_week):
    # Übersicht erweiterten Marktstatus
    ax = df.set_index("Kreis")[[
        "Aktive Käufer:innen",
        "Potentielle Käufer:innen",
        "Aktive Verkäufer:innen (Listings)",
        "Potentielle Verkäufer:innen"
    ]].plot(
        kind="bar",
        figsize=(16, 8),
        stacked=True
    )
    plt.title(f"Marktübersicht Zürich – Kalenderwoche {current_week}")
    plt.ylabel("Anzahl Agent:innen")
    plt.xlabel("Kreis")
    plt.legend(title="Agententypen", loc="upper right")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def generate_early_warnings(market_df, demand_threshold=1.5, supply_threshold=2):
    warnings = []

    for _, row in market_df.iterrows():
        kreis = row['Kreis']
        buyers = row['Aktive Käufer:innen']
        sellers = row['Aktive Verkäufer:innen (Listings)']

        # Keine Warnung, wenn überhaupt keine Marktaktivität
        if buyers == 0 and sellers == 0:
            continue

        if sellers == 0 and buyers >= supply_threshold:
            warnings.append(f"⚡ Kein Angebot in Kreis {kreis}, aber {buyers} aktive Käufer:innen!")
        else:
            demand_supply_ratio = buyers / (sellers + 1e-5)
            if demand_supply_ratio > demand_threshold:
                warnings.append(f"🚨 Hohe Nachfrage in Kreis {kreis}: {buyers} Käufer:innen auf {sellers} Angebote (Ratio: {demand_supply_ratio:.2f})")

    return warnings
