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
        self.status = "active"  # 🟢 Korrekt: Käufer:innen starten als aktiv!

    # --- Neue individuelle Präferenzen ---
        self.min_area = random.uniform(70, 120)  # Wunsch: mindestens 70–120 m2
        self.prefers_new_building = random.choice([True, False])  # Neubau ja/nein


    def step(self):
        # --- Aktivierung basierend auf Google Trends und Luxuskonsum ---
        if self.model.current_week < len(self.model.buy_trends):
            impulse = float(self.model.buy_trends[self.model.current_week])
            luxury = float(self.model.luxury_trends[self.model.current_week])
        else:
            impulse = 0.3  # Fallback
            luxury = 0.3

        # Aktivitätslevel berechnen
        activity_level = impulse * self.preference_score * (1 + 0.2 * luxury)
        self.active = random.random() < activity_level

        # --- Immobilie suchen ---
        if self.active:
            listings = [
                a for a in self.model.schedule.agents
                if hasattr(a, "listed") and a.listed and a.location == self.location and a.price <= self.budget
            ]
            if listings:
                chosen = self.random.choice(listings)
                self.model.broker.mediate_transaction(self, chosen)