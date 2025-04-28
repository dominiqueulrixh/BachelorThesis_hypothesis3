from mesa import Agent

class CityAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # Eingreifen nur bei extremen Bedingungen
        if self.model.current_week > 5:  # Nicht gleich am Anfang
            high_interest = self.model.bank.current_interest_rate > 3.0
            low_demand = sum(1 for a in self.model.schedule.agents if hasattr(a, "active") and a.active) < 5

            if high_interest or low_demand:
                self.initiate_market_support()

    def initiate_market_support(self):
        # Stadt könnte z.B. symbolische Subventionen für Käufer:innen einführen
        # In Modell: Luxusfaktor leicht anheben, um Nachfrage wieder anzuregen
        if self.model.current_week < len(self.model.luxury_trends):
            self.model.luxury_trends[self.model.current_week] = min(100, self.model.luxury_trends[self.model.current_week] + 5)

        print(f"🏛️ CityAgent: Marktintervention in Woche {self.model.current_week} aktiviert!")
