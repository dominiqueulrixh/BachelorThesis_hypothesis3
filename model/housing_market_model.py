from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from agents.buyer_agent import BuyerAgent
from agents.seller_agent import SellerAgent
from agents.potentialSeller_agent import PotentialSellerAgent
from agents.broker_agent import BrokerAgent
from agents.bank_agent import BankAgent
from agents.city_agent import CityAgent

from data.data_loader import load_population_data, load_income_data, load_building_data, load_trends_data
from utils.person_profile import PersonProfile
from utils.property_valuation import estimate_price

import random
import numpy as np

class HousingMarketModel(Model):
    def __init__(self, n_buyers=20, n_sellers=5, n_potential_sellers=10):
        self.schedule = RandomActivation(self)
        self.num_agents = 0
        self.current_week = 0

        self.interest_rate_trend = np.linspace(2.5, 1.5, 52)  # Zinssenkung über das Jahr

        # --- Daten laden ---
        self.population_data = load_population_data()
        self.income_data = load_income_data()
        self.building_data = load_building_data()
        self.buy_trends, self.luxury_trends = load_trends_data()

        # --- Agenten erstellen ---

        # BankAgent: Zinspolitik
        self.bank = BankAgent(self.num_agents, self, self.interest_rate_trend)
        self.schedule.add(self.bank)
        self.num_agents += 1

        # CityAgent: Städteplanung
        self.city = CityAgent(self.num_agents, self)
        self.schedule.add(self.city)
        self.num_agents += 1

        # BrokerAgent: Vermittlung
        self.broker = BrokerAgent(self.num_agents, self)
        self.schedule.add(self.broker)
        self.num_agents += 1

        # Käufer:innen (BuyerAgents)
        for _ in range(n_buyers):
            profile = self.generate_person_profile(buyer=True)
            preference_score = random.uniform(0, 1)
            buyer = BuyerAgent(self.num_agents, self, profile, preference_score)
            self.schedule.add(buyer)
            self.num_agents += 1

        # Verkäufer:innen (SellerAgents)
        for _ in range(n_sellers):
            building_info = self.sample_building_info()
            seller_age = random.randint(30, 90)
            seller = SellerAgent(self.num_agents, self, building_info, seller_age)
            self.schedule.add(seller)
            self.num_agents += 1

        # Potentielle Verkäufer:innen (PotentialSellerAgents)
        for _ in range(n_potential_sellers):
            expected_building_info = self.sample_building_info()
            potential_seller = PotentialSellerAgent(self.num_agents, self, expected_building_info)
            self.schedule.add(potential_seller)
            self.num_agents += 1

        # --- DataCollector für Simulationsergebnisse ---
        self.datacollector = DataCollector(
            model_reporters={
                "Verkäufe": lambda m: m.broker.completed_sales,
                "Angebot": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, SellerAgent) and a.listed and a.status == "active"),
                "Nachfrage": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, BuyerAgent) and a.active and a.status == "active"),
                "Zinsniveau": lambda m: m.bank.current_interest_rate,
                "LuxuskonsumIndex": lambda m: m.luxury_trends[m.current_week] if m.current_week < len(m.luxury_trends) else 50
            }
        )

    def generate_person_profile(self, buyer=True):
        """Erstellt realistisches PersonProfile für Käufer oder Verkäufer."""
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

        # Einkommen aus passendem Kreis UND passendem SteuerTarif wählen
        income_rows = self.income_data[self.income_data['KreisCd'] == kreis]

        if buyer:
            # Käufer:innen: eher SteuerTarifCd 0 (Single) oder 1 (Verheiratet)
            income_rows = income_rows[income_rows['SteuerTarifCd'].isin([0, 1])]
        else:
            # Verkäufer:innen: auch SteuerTarifCd 1 oder 2 (Familien)
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
        """Zufälliges realistisches Gebäude auswählen + Fläche jittern."""
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

        # Jitter Fläche: ±10m² (float)
        jitter = np.random.uniform(-10, 10)
        adjusted_single_building_area = max(10, single_building_area + jitter)

        return {
            "KreisCd": int(building_row['KreisCd']),
            "BauperiodeLevel1Lang": building_row['BauperiodeLevel1Lang'],
            "GbdFlaecheAufN": float(adjusted_single_building_area)
        }

    def step(self):
        """Ein Simulationsschritt: Alle Agenten bewegen sich, neue treten auf, Verkäufe geschehen."""
        self.datacollector.collect(self)
        self.schedule.step()
        self.current_week += 1

        if self.current_week % 4 == 0:  # jeden Monat neue Akteure
            self.add_new_buyers(5)
            self.add_new_sellers(2)

        self.age_sellers()

    def register_sale(self, buyer, seller):
        seller.listed = False
        seller.status = "sold"
        buyer.status = "completed"
        self.broker.completed_sales += 1

    def get_price_trend(self):
        return 0.02 / 52  # konstante Preissteigerung 2% p.a.

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
