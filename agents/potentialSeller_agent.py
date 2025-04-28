from mesa import Agent
import random
from utils.property_valuation import estimate_price
from agents.seller_agent import SellerAgent
from agents.buyer_agent import BuyerAgent



class PotentialSellerAgent(Agent):
    def __init__(self, unique_id, model, expected_building_info):
        super().__init__(unique_id, model)
        self.location = expected_building_info['KreisCd']
        self.area = expected_building_info['GbdFlaecheAufN']
        self.build_year_category = expected_building_info['BauperiodeLevel1Lang']
        self.expected_price = estimate_price(self.location, self.build_year_category, self.area)
        self.ready_to_sell = False
        self.status = "active"  # 🟢 Korrekt: Start als aktiv!

    def step(self):
        active_buyers = sum(
            1 for a in self.model.schedule.agents if isinstance(a, BuyerAgent) and a.active
        )
        active_listings = sum(
            1 for a in self.model.schedule.agents if isinstance(a, SellerAgent) and a.listed
        )

        demand_supply_ratio = active_buyers / (active_listings + 1)
        price_trend = self.model.get_price_trend()

        if self.model.current_week < len(self.model.luxury_trends):
            luxury_factor = float(self.model.luxury_trends[self.model.current_week]) / 100
        else:
            luxury_factor = 0.5

        decision_score = demand_supply_ratio + price_trend + 0.2 * luxury_factor

        if decision_score > 1.8:
            if self.random.random() < 0.6:
                self.list_property()

    def list_property(self):
        seller_age = random.randint(30, 90)
        new_listing = SellerAgent(
            self.model.num_agents,
            self.model,
            {
                'KreisCd': self.location,
                'BauperiodeLevel1Lang': self.build_year_category,
                'GbdFlaecheAufN': self.area
            },
            seller_age
        )
        self.model.schedule.add(new_listing)
        self.model.num_agents += 1
        self.ready_to_sell = True
