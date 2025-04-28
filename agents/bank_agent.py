from mesa import Agent
import random

class BankAgent(Agent):
    def __init__(self, unique_id, model, interest_rate_trend):
        super().__init__(unique_id, model)
        self.interest_rate_trend = interest_rate_trend
        self.current_interest_rate = interest_rate_trend[0]  # Startwert

    def step(self):
        # Fortschreibung des Zinsniveaus
        if self.model.current_week < len(self.interest_rate_trend):
            base_rate = self.model.interest_rate_trend[self.model.current_week]
        else:
            base_rate = self.model.interest_rate_trend[-1]

        # Kleine Zufallsschwankungen simulieren
        random_fluctuation = random.uniform(-0.05, 0.05)
        self.current_interest_rate = max(0, base_rate + random_fluctuation)
