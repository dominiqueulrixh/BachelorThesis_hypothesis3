from mesa import Agent
from agents.buyer_agent import BuyerAgent
from agents.seller_agent import SellerAgent
import pandas as pd
import random


class BrokerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.completed_sales = 0

    def mediate_transaction(self, buyer, seller):
        if buyer.budget * 1.2 >= seller.price:
            self.model.register_sale(buyer, seller)
            self.completed_sales += 1

    def step(self):
        pass

    def suggest_matches(self):
        suggestions = []

        active_buyers = [
            agent for agent in self.model.schedule.agents
            if isinstance(agent, BuyerAgent) and agent.active and agent.status == "active"
        ]

        active_sellers = [
            agent for agent in self.model.schedule.agents
            if isinstance(agent, SellerAgent) and agent.listed and agent.status == "active"
        ]

        if not active_buyers:
            print("❗ Keine aktiven Käufer gefunden.")
        if not active_sellers:
            print("❗ Keine aktiven Verkäufer gefunden.")

        for buyer in active_buyers:
            best_match = None
            best_score = 0

            for seller in active_sellers:
                comments = []

                # Preis über harte Grenze?
                if seller.price > buyer.budget * 1.1:
                    continue

                # --- Einzel-Scores ---
                # Preis-Score
                preis_diff = abs(seller.price - buyer.budget) / buyer.budget
                if preis_diff < 0.02:
                    preis_score = 100
                elif preis_diff < 0.05:
                    preis_score = 90
                elif preis_diff < 0.10:
                    preis_score = 75
                else:
                    preis_score = 50
                    comments.append("Preis über Budget")

                # Standort-Score
                if buyer.location == seller.location:
                    standort_score = 100
                else:
                    standort_score = 70
                    comments.append("Standortabweichung")

                # Flächen-Score
                if seller.area >= buyer.min_area:
                    flaeche_score = 100
                else:
                    flaeche_score = 60
                    comments.append("Fläche kleiner als Wunschfläche")

                # Bauperiode-Score
                if buyer.prefers_new_building:
                    if any(x in seller.build_year_category for x in ["2000", "2010", "2020"]):
                        bau_score = 100
                    else:
                        bau_score = 70
                        comments.append("Neubau bevorzugt")
                else:
                    if any(x in seller.build_year_category for x in ["Vor 1893", "1893 - 1949"]):
                        bau_score = 100
                    else:
                        bau_score = 70
                        comments.append("Altbau bevorzugt")

                # --- Gesamtscore als gewichteter Durchschnitt ---
                final_score = (preis_score * 0.5 + standort_score * 0.2 +
                               flaeche_score * 0.2 + bau_score * 0.1)

                # Bester Match für diesen Käufer merken
                if final_score > best_score:
                    best_score = final_score
                    best_match = {
                        "BuyerID": buyer.unique_id,
                        "BuyerBudget": round(buyer.budget),
                        "BuyerKreis": buyer.location,
                        "SellerID": seller.unique_id,
                        "OfferPrice": round(seller.price),
                        "SellerKreis": seller.location,
                        "MatchingScore": round(final_score, 2),
                        "ViaBroker": random.choice([True, False]),
                        "FinalPrice": round(seller.price * (1.02 if random.random() > 0.5 else 1.0)),
                        "Comments": comments,
                        "Gelisted": seller.listed  # NEU: Gelistet-Status ins Matching aufnehmen

                    }

            if best_match and best_match["MatchingScore"] >= 50:
                suggestions.append(best_match)

        return suggestions

    @staticmethod
    def create_matching_dataframe(matches):
        df = pd.DataFrame(matches)
        if not df.empty:
            df = df.sort_values(by="MatchingScore", ascending=False)
        return df