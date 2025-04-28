from mesa import Agent
import random
from utils.person_profile import PersonProfile

class BuyerAgent(Agent):
    def __init__(self, unique_id, model, profile: PersonProfile, preference_score):
        super().__init__(unique_id, model)
        self.profile = profile
        self.budget = profile.budget
        self.location = profile.kreis
        self.preference_score = preference_score
        self.active = False
        self.prefers_broker = random.random() < 0.7  # 70% bevorzugen Broker
        self.status = "active"

    # Neue individuelle Präferenzen
        self.min_area = random.uniform(70, 120)  # Wunsch: mindestens 70–120 m2
        self.prefers_new_building = random.choice([True, False])  # Neubau ja/nein


    def step(self):
        # Aktivierung basierend auf Google Trends und Luxuskonsum
        if self.model.current_week < len(self.model.buy_trends):
            impulse = float(self.model.buy_trends[self.model.current_week])
            if self.model.current_week < len(self.model.luxury_trends):
                luxury = float(self.model.luxury_trends[self.model.current_week])
            else:
                luxury = float(self.model.luxury_trends[-1])
        else:
            impulse = 0.3
            luxury = 0.3

        # Aktivitätslevel berechnen
        activity_level = impulse * self.preference_score * (1 + 0.2 * luxury)
        self.active = random.random() < activity_level

        # Immobilie suchen
        if self.active:
            listings = [
                a for a in self.model.schedule.agents
                if hasattr(a, "listed") and a.listed and a.location == self.location and a.price <= self.budget
            ]
            if listings:
                chosen = self.random.choice(listings)
                self.model.broker.mediate_transaction(self, chosen)

    def adjust_activity_based_on_interest_rate(self, current_interest_rate):
        # Passt die Aktivität des Käufers basierend auf dem aktuellen Zinsniveau an.
        if current_interest_rate < 1.5:
            self.active = True
        elif 1.5 <= current_interest_rate < 2.5:
            self.active = random.random() > 0.10
        elif 2.5 <= current_interest_rate < 3.5:
            self.active = random.random() > 0.30
        else:
            self.active = random.random() > 0.50
