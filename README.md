# Hypothese 3 – Prognoseverbesserung durch heterogene Agententypen & Datenquellen

Diese Simulation überprüft die Hypothese, dass durch die Kombination unterschiedlicher Agententypen sowie die Integration vielfältiger strukturierter, verhaltens- und makroökonomischer Datenquellen die Prognosegüte von Angebot und Nachfrage auf dem Immobilienmarkt verbessert werden kann. Das Modell bildet eine erweiterte und realitätsnahe Version des Immobilienmarkts auf Agentenbasis ab.

---

## Ziel der Hypothese

> Die Kombination heterogener Agententypen mit externen verhaltens- und strukturbezogenen Datenquellen innerhalb eines Multi-Agenten-Systems führt zu einer Verbesserung der Vorhersagequalität von Angebot und Nachfrage auf dem Immobilienmarkt.

Zentrale Erweiterungen im Vergleich zu Hypothese 1 und 2:

- Einführung neuer Agententypen (`PotentialSellerAgent`, `BankAgent`)
- Regionale Parametrisierung durch reale Daten (Einkommen, Bevölkerung, Gebäudestruktur)
- Dynamische Aktivierung durch Google-Trends und Zinsniveau

---

## Modellübersicht

| Komponente              | Beschreibung                                                                 |
|--------------------------|------------------------------------------------------------------------------|
| `BuyerAgent`             | Kaufinteressierte, aktiviert durch Trendsignale & beeinflusst durch Zinslage |
| `SellerAgent`            | Anbieter mit fixem Verkaufsangebot                                           |
| `PotentialSellerAgent`   | Passiv bis zur Aktivierung durch Marktimpulse (z. B. Preisniveau)            |
| `BankAgent`              | Modelliert Zinssatzdynamik, beeinflusst Kaufkraft                            |
| `BrokerAgent`            | Vermittlung zwischen Käufer und Verkäufer                                    |
| `HousingMarketModel`     | Gesamtsteuerung der Agenten, Matching, Datenfluss                            |
| `data_loader.py`         | Einbindung externer Datenquellen (CSV-Dateien)                               |
| `property_valuation.py`  | Standort- und objektbasierte Preisbewertung                                  |
| `person_profile.py`      | Soziodemografisches Käuferprofil (Budgetvergabe nach Regionseinkommen)       |

---

## Methodik

- Verknüpfung strukturierter Daten:
  - `einkommenZuerich.csv`, `bevoelkerungZuerich.csv`, `gebaeudeZuerich.csv`
- Integration verhaltensbasierter Indikatoren:
  - Google-Suchtrends (Käuferseite)
- Einbindung makroökonomischer Faktoren:
  - Zinsentwicklung (über `BankAgent`)
- Regionale Differenzierung:
  - Agentenverhalten ist standortspezifisch parametrisiert
- Erweiterte Angebotslogik:
  - Potenzielle Verkäufer werden aktiv bei Marktüberhitzung

---

## Ergebnisse

- Zinsgesteuerte Aktivierung zeigt kausale Zusammenhänge zwischen Finanzierungskosten und Nachfrageintensität
- Dynamische Angebotsentwicklung durch `PotentialSellerAgents` wirkt stabilisierend auf Marktspannung
- Marktspannungsanalyse zeigt realitätsnahe zyklische Ungleichgewichte
- Matching-Logik verbessert, da Angebot & Nachfrage zeitlich korrelieren

> Fazit: Das Modell erlaubt eine differenzierte, verhaltenssensitive Abbildung der Marktdynamik und bildet Angebot und Nachfrage realitätsnäher ab als in den Vorläuferhypothesen.

---

## Dateien im Projektordner (Auswahl)

| Datei                          | Funktion                                                                 |
|--------------------------------|--------------------------------------------------------------------------|
| `main.py`                      | Simulationseintrittspunkt (Jupyter & CLI)                                |
| `housing_market_model.py`      | Modelllogik & Agentenerstellung                                          |
| `buyer_agent.py`, `seller_agent.py` | Agentenverhalten der Käufer und Verkäufer                           |
| `potentialSeller_agent.py`     | Reaktive Angebotsseite: neue Verkäufer werden aktiviert                 |
| `bank_agent.py`                | Modellierung von Zinsschwankungen                                        |
| `GoogleTrendsLoader.py`        | Verhaltensdatenimport zur Käuferaktivierung                              |
| `data_loader.py`               | Einlesen externer Marktdaten (Einkommen, Gebäude etc.)                   |
| `app.py`, `backend.py`         | Streamlit-Frontend zur Ergebnisdarstellung & Modellsteuerung             |

---

## Frontend starten (Streamlit)

Du kannst das Modell über eine interaktive Oberfläche ausführen und analysieren. So startest das Streamlit-Frontend lokal:

### Voraussetzungen

Stelle sicher, dass `streamlit` installiert ist:

```bash 
pip install streamlit
```

### Starten

Wechsle in das Verzeichnis, das `app.py` enthält, und führe folgenden Befehl aus:

```bash 
streamlit run app.py
```

Die App öffnet sich automatisch im Browser. 

---

### Visualisierungen & Analysen

- Käuferaktivierungsrate unter verschiedenen Zinsszenarien
- Nachfrage- vs. Angebotsverhältnis (Marktspannung)
- Matching-Effizienz und Transaktionsverläufe
- Entwicklung von Angebot und Nachfrage über Raum und Zeit

---

### Weiterführend

Die Simulation verbindet alle Erkenntnisse aus Hypothese 1 (Grundmodell) und Hypothese 2 (verhaltensbasierte Steuerung) zu einem integrierten, datengetriebenen Multi-Agenten-System für den Immobilienmarkt.
