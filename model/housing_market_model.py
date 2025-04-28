from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from agents.buyer_agent import BuyerAgent
from agents.seller_agent import SellerAgent
from agents.potentialSeller_agent import PotentialSellerAgent
from agents.broker_agent import BrokerAgent
from agents.bank_agent import BankAgent
from agents.test_agent import TestAgent

from data.data_loader import load_population_data, load_income_data, load_building_data, load_trends_data
from utils.person_profile import PersonProfile

import random
import numpy as np

class HousingMarketModel(Model):
    def __init__(self, n_buyers=20, n_sellers=5, n_potential_sellers=10):
        self.schedule = RandomActivation(self)
        self.num_agents = 0
        self.current_week = 0

        # Zinssenkung über Jahr
        self.interest_rate_trend = np.linspace(2.5, 1.5, 52)

        # Daten laden
        self.population_data = load_population_data()
        self.income_data = load_income_data()
        self.building_data = load_building_data()
        self.buy_trends, self.luxury_trends = load_trends_data()

        # Agenten erstellen

        # BankAgent: Zinspolitik
        self.bank = BankAgent(self.num_agents, self, self.interest_rate_trend)
        self.schedule.add(self.bank)
        self.num_agents += 1

        # BrokerAgent: Vermittlung
        self.broker = BrokerAgent(self.num_agents, self)
        self.schedule.add(self.broker)
        self.num_agents += 1

        # BuyerAgents
        for _ in range(n_buyers):
            profile = self.generate_person_profile(buyer=True)
            preference_score = random.uniform(0, 1)
            buyer = BuyerAgent(self.num_agents, self, profile, preference_score)
            self.schedule.add(buyer)
            self.num_agents += 1

        # SellerAgents
        for _ in range(n_sellers):
            building_info = self.sample_building_info()
            seller_age = random.randint(30, 90)
            seller = SellerAgent(self.num_agents, self, building_info, seller_age)
            self.schedule.add(seller)
            self.num_agents += 1

        # PotentialSellerAgents
        for _ in range(n_potential_sellers):
            expected_building_info = self.sample_building_info()
            potential_seller = PotentialSellerAgent(self.num_agents, self, expected_building_info)
            self.schedule.add(potential_seller)
            self.num_agents += 1

        # DataCollector für Simulationsergebnisse
        self.datacollector = DataCollector(
            model_reporters={
                "Verkäufe": lambda m: m.broker.completed_sales,
                "Angebot": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, SellerAgent) and a.listed and a.status == "active"),
                "Nachfrage": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, BuyerAgent) and a.active and a.status == "active"),
                "Zinsniveau": lambda m: m.bank.current_interest_rate,
                "LuxuskonsumIndex": lambda m: m.luxury_trends[m.current_week] if m.current_week < len(m.luxury_trends) else 50,
                "Potenzielle Verkäufer": lambda m: sum(
                    1 for a in m.schedule.agents if isinstance(a, SellerAgent) and not a.listed and a.status == "active"
                )
            }
        )

        # TestAgent hinzufügen
        self.test_agent = TestAgent(self.num_agents, self)
        self.schedule.add(self.test_agent)
        self.num_agents += 1

    def generate_person_profile(self, buyer=True):
        if buyer:
            valid_ages = ["30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69"]
        else:
            valid_ages = ["45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85-89"]

        filtered_population = self.population_data[
            self.population_data['AgeGroup'].isin(valid_ages)
        ]

        if filtered_population.empty:
            person_row = self.population_data.sample(1).iloc[0]
        else:
            person_row = filtered_population.sample(1).iloc[0]

        kreis = int(person_row['Kreis'])

        income_rows = self.income_data[self.income_data['KreisCd'] == kreis]

        if buyer:
            income_rows = income_rows[income_rows['SteuerTarifCd'].isin([0, 1])]
        else:
            income_rows = income_rows[income_rows['SteuerTarifCd'].isin([1, 2])]

        if income_rows.empty:
            income_row = self.income_data.sample(1).iloc[0]
        else:
            income_row = income_rows.sample(1).iloc[0]

        return PersonProfile(
            age=person_row['AgeGroup'],
            sex=person_row['Sex'],
            origin=person_row['Origin'],
            kreis=kreis,
            income_p50=income_row['SteuerEinkommen_p50'],
            income_p25=income_row['SteuerEinkommen_p25'],
            income_p75=income_row['SteuerEinkommen_p75']
        )

    def sample_building_info(self):
        valid_buildings = self.building_data[
            (self.building_data['GbdFlaecheAufN'] > 0) &
            (self.building_data['GbdFlaecheAufN'] / self.building_data['AnzGbd'] < 150) &
            (self.building_data['GbdFlaecheAufN'] / self.building_data['AnzGbd'] * 12000 < 1_500_000)
        ]

        if valid_buildings.empty:
            building_row = self.building_data.sample(1).iloc[0]
        else:
            building_row = valid_buildings.sample(1).iloc[0]

        gesamtfläche = building_row['GbdFlaecheAufN']
        anzahl_gebäude = building_row['AnzGbd']

        if anzahl_gebäude > 0:
            single_building_area = gesamtfläche / anzahl_gebäude
        else:
            single_building_area = gesamtfläche

        jitter = np.random.uniform(-10, 10)
        adjusted_single_building_area = max(10, single_building_area + jitter)

        return {
            "KreisCd": int(building_row['KreisCd']),
            "BauperiodeLevel1Lang": building_row['BauperiodeLevel1Lang'],
            "GbdFlaecheAufN": float(adjusted_single_building_area)
        }

    def step(self):
        self.current_week += 1

        for agent in self.schedule.agents:
            if isinstance(agent, BuyerAgent):
                agent.adjust_activity_based_on_interest_rate(self.bank.current_interest_rate)

        if self.current_week % 4 == 0:
            self.add_new_buyers(5)
            self.add_new_sellers(2)

        self.age_sellers()
        self.schedule.step()
        self.datacollector.collect(self)

    def register_sale(self, buyer, seller):
        seller.listed = False
        seller.status = "sold"
        buyer.status = "completed"
        self.broker.completed_sales += 1

    def get_price_trend(self):
        return 0.02 / 52

    def add_new_buyers(self, n):
        for _ in range(n):
            profile = self.generate_person_profile(buyer=True)
            buyer = BuyerAgent(self.num_agents, self, profile, random.uniform(0, 1))
            self.schedule.add(buyer)
            self.num_agents += 1

    def add_new_sellers(self, n):
        for _ in range(n):
            building_info = self.sample_building_info()
            seller_age = random.randint(30, 90)
            seller = SellerAgent(self.num_agents, self, building_info, seller_age)
            self.schedule.add(seller)
            self.num_agents += 1

    def age_sellers(self):
        for agent in self.schedule.agents:
            if isinstance(agent, SellerAgent) and agent.status == "active":
                agent.age += 1 / 52
                if agent.age >= 70:
                    agent.forced_broker = True