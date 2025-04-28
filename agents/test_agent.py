from mesa import Agent

from agents.buyer_agent import BuyerAgent
from scipy.stats import ttest_ind


class TestAgent(Agent):

    # Testagent zur Durchführung von Experimentszenarien
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.active = True
        self.test_results = {
            "konstanter_zins_aktivierungsrate": [],
            "sinkender_zins_aktivierungsrate": []
        }

    def step(self):
        # Nichts tun - Tests werden manuell durch Aufruf gestartet
        pass

    def run_zins_test(self):
        # zwei Szenarien: Konstanter vs. sinkender Zins
        results = {}

        # Szenario 1: Konstanter Zinssatz
        konstanter_zins = [2.5] * 52
        activation_const = self.run_simulation_with_zins(konstanter_zins)
        results["konstanter_zins"] = activation_const

        # Szenario 2: Sinkender Zinssatz
        import numpy as np
        sinkender_zins = np.linspace(2.5, 1.5, 52).tolist()
        activation_sink = self.run_simulation_with_zins(sinkender_zins)
        results["sinkender_zins"] = activation_sink

        self.test_results = results

    def run_simulation_with_zins(self, zinsverlauf):
        # Hilfsfunktion: Minisimulation unter spezifiziertem Zinsverlauf
        from model.housing_market_model import HousingMarketModel

        temp_model = HousingMarketModel(n_buyers=20, n_sellers=5, n_potential_sellers=10)
        temp_model.interest_rate_trend = zinsverlauf
        temp_model.bank.interest_rate_trend = zinsverlauf

        activation_rates = []

        for _ in range(52):
            temp_model.step()
            buyers = sum(
                1 for a in temp_model.schedule.agents
                if isinstance(a, BuyerAgent) and a.active and a.status == "active"
            )
            all_buyers = sum(
                1 for a in temp_model.schedule.agents
                if isinstance(a, BuyerAgent) and a.status == "active"
            )
            activation = buyers / all_buyers if all_buyers > 0 else 0
            activation_rates.append(activation)

        return activation_rates

    def plot_results(self):
        #Plottet die Vergleichsergebnisse
        import matplotlib.pyplot as plt

        konst = self.test_results.get("konstanter_zins", [])
        sink = self.test_results.get("sinkender_zins", [])

        plt.figure(figsize=(12, 6))
        plt.plot(konst, label="Konstanter Zins (2.5%)", linestyle="--", color="red")
        plt.plot(sink, label="Sinkender Zins (2.5% → 1.5%)", linestyle="-", color="green")
        plt.title("🎯 Käufer:innen Aktivierungsrate – Einfluss des Zinsniveaus (TestAgent)")
        plt.xlabel("Kalenderwoche")
        plt.ylabel("Aktivierungsrate")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def run_t_test(self):
        # t-Test auf Käuferaktivierungsraten & interpretation
        konst = self.test_results.get("konstanter_zins", [])
        sinkend = self.test_results.get("sinkender_zins", [])

        if not konst or not sinkend:
            print("❗ Testdaten fehlen. Bitte zuerst 'run_zins_test()' ausführen.")
            return

        # t-Test
        t_stat, p_value = ttest_ind(sinkend, konst, equal_var=False)

        print("\n📊 Ergebnisse des t-Tests:")
        print(f"t-Statistik: {t_stat:.3f}")
        print(f"p-Wert: {p_value:.2e}")

        # Interpretation
        alpha = 0.05
        if p_value < alpha:
            print("✅ Unterschied ist statistisch signifikant: Sinkender Zins beeinflusst die Käuferaktivierung.")
        else:
            print("❌ Unterschied ist nicht statistisch signifikant: Kein klarer Einfluss nachweisbar.")


    def run_behavioral_data_test(self):
        # Vergleicht Käuferaktivierung mit und ohne verhaltensbasierte Daten
        from model.housing_market_model import HousingMarketModel

        results = {}

        # Simulation 1: MIT verhaltensbasierten Daten
        model_with_behavior = HousingMarketModel(n_buyers=20, n_sellers=5, n_potential_sellers=10)
        model_with_behavior.interest_rate_trend = [2.0] * 52
        model_with_behavior.bank.interest_rate_trend = [2.0] * 52

        activation_behavior = []
        for _ in range(52):
            model_with_behavior.step()
            buyers = sum(
                1 for a in model_with_behavior.schedule.agents
                if isinstance(a, BuyerAgent) and a.active and a.status == "active"
            )
            all_buyers = sum(
                1 for a in model_with_behavior.schedule.agents
                if isinstance(a, BuyerAgent) and a.status == "active"
            )
            activation = buyers / all_buyers if all_buyers > 0 else 0
            activation_behavior.append(activation)

        results["mit_verhaltensdaten"] = activation_behavior

        # Simulation 2: OHNE verhaltensbasierte Daten
        model_without_behavior = HousingMarketModel(n_buyers=20, n_sellers=5, n_potential_sellers=10)
        model_without_behavior.interest_rate_trend = [2.0] * 52
        model_without_behavior.bank.interest_rate_trend = [2.0] * 52

        model_without_behavior.buy_trends = [0.5] * 52
        model_without_behavior.luxury_trends = [0.5] * 52

        activation_no_behavior = []
        for _ in range(52):
            model_without_behavior.step()
            buyers = sum(
                1 for a in model_without_behavior.schedule.agents
                if isinstance(a, BuyerAgent) and a.active and a.status == "active"
            )
            all_buyers = sum(
                1 for a in model_without_behavior.schedule.agents
                if isinstance(a, BuyerAgent) and a.status == "active"
            )
            activation = buyers / all_buyers if all_buyers > 0 else 0
            activation_no_behavior.append(activation)

        results["ohne_verhaltensdaten"] = activation_no_behavior

        self.test_results_behavior = results

        print("\n✅ Behavioral Data Test abgeschlossen – Ergebnisse gespeichert.")


    def run_behavioral_t_test(self):
        """Führt einen t-Test für den Behavioral Data Test durch."""
        from scipy.stats import ttest_ind

        if not hasattr(self, "test_results_behavior"):
            print("❗ Bitte zuerst 'run_behavioral_data_test()' ausführen!")
            return

        with_behavior = self.test_results_behavior.get("mit_verhaltensdaten", [])
        without_behavior = self.test_results_behavior.get("ohne_verhaltensdaten", [])

        t_stat, p_value = ttest_ind(with_behavior, without_behavior, equal_var=False)

        print("\n📊 Ergebnisse des t-Tests für verhaltensbasierte Daten:")
        print(f"t-Statistik: {t_stat:.3f}")
        print(f"p-Wert: {p_value:.2e}")

        alpha = 0.05
        if p_value < alpha:
            print("✅ Verhaltensbasierte Daten haben signifikant Einfluss auf die Käuferaktivierung!")
        else:
            print("❌ Kein signifikanter Einfluss von Verhaltensdaten feststellbar.")
