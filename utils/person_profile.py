import random

class PersonProfile:
    def __init__(self, age, sex, origin, kreis, income_p50, income_p25, income_p75):
        self.age = age
        self.sex = sex
        self.origin = origin
        self.kreis = kreis
        self.income = self.estimate_income(income_p50, income_p25, income_p75)
        self.budget = self.estimate_budget()

    def estimate_income(self, p50, p25, p75):
        """Zufälliges Einkommen innerhalb der Verteilung schätzen."""
        return random.uniform(p25, p75)

    def estimate_budget(self):
        """Typisches Kaufbudget: Einkommen × Faktor."""
        factor = random.uniform(10, 14)  # mehr realistische Kaufkraft für Zürich
        return self.income * 1000 * factor
