import random

def estimate_price(kreis, bauperiode, flaeche):
    # Basispreise nach Kreis
    base_price_by_kreis = {
        1: 17000, 2: 16000, 3: 15000, 4: 14000,
        5: 13000, 6: 12000, 7: 11500, 8: 11000,
        9: 10500, 10: 10000, 11: 9500, 12: 9000
    }
    base_price = base_price_by_kreis.get(kreis, 10000)

    # Bauperioden
    if "Vor 1893" in bauperiode or "1893 - 1899" in bauperiode:
        modifier = 1.05
    elif "1970 - 1989" in bauperiode:
        modifier = 0.9
    elif "1950 - 1969" in bauperiode:
        modifier = 0.85
    elif "2010" in bauperiode or "2020" in bauperiode:
        modifier = 1.1
    else:
        modifier = 1.0

    # Basispreis berechnen
    price = flaeche * base_price * modifier

    # Preis plusMinus 5%
    price_jitter = random.uniform(-0.05, 0.05)
    price *= (1 + price_jitter)

    # Mindestpreis
    if price < 450000:
        price = 450000

    return round(price)
