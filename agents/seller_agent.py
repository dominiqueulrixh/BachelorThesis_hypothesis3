from mesa import Agent
import random
from utils.property_valuation import estimate_price

class SellerAgent(Agent):
    def __init__(self, unique_id, model, building_info, age):
        super().__init__(unique_id, model)
        self.location = building_info['KreisCd']
        self.area = building_info['GbdFlaecheAufN']
        self.build_year_category = building_info['BauperiodeLevel1Lang']
        self.price = min(estimate_price(self.location, self.build_year_category, self.area), 2_500_000)
        self.listed = True
        self.status = "active"
        self.age = age
        self.forced_broker = age >= 70  # Verkaufsdruck bei Alter >= 70

    def step(self):
        if not self.listed:
            return

        active_buyers = sum(
            1 for a in self.model.schedule.agents if hasattr(a, "active") and a.active
        )

        if self.model.current_week < len(self.model.luxury_trends):
            luxury_factor = float(self.model.luxury_trends[self.model.current_week]) / 100
        else:
            luxury_factor = 0.5

        sell_pressure = (active_buyers / (1 + active_buyers)) + 0.2 * luxury_factor

        if random.random() < sell_pressure * 0.05:
            self.listed = False  # Immobilie wird entfernt (verkauft/abgezogen)
