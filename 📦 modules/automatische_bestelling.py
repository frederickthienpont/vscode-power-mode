from datetime import datetime, timedelta
import json
import os
from typing import List
from modules import voorraadbeheer, verkoopgeschiedenis

BESTELLING_FILE = "data/automatische_bestellingen.json"

class AutomatischeBestelling:
    def __init__(self, artikel_id, aantal_bestellen, bestelling_datum):
        self.artikel_id = artikel_id
        self.aantal_bestellen = aantal_bestellen
        self.bestelling_datum = bestelling_datum

def laad_automatische_bestellingen() -> List[AutomatischeBestelling]:
    if not os.path.exists(BESTELLING_FILE):
        return []
    with open(BESTELLING_FILE, "r") as f:
        data = json.load(f)
    return [AutomatischeBestelling(**b) for b in data]

def opslaan_automatische_bestellingen(bestellingen: List[AutomatischeBestelling]):
    with open(BESTELLING_FILE, "w") as f:
        json.dump([b.__dict__ for b in bestellingen], f, indent=2, default=str)

def voorspellen_bestelling(artikel_id: int, periode: int = 30) -> int:
    verkoop = verkoopgeschiedenis.laad_verkoopgeschiedenis()
    verkopen = [v for v in verkoop if v.artikel_id == artikel_id and v.verkoop_datum > datetime.now() - timedelta(days=periode)]
    
    totaal_verkocht = sum([v.aantal for v in verkopen])
    gemiddelde_verkoop_per_dag = totaal_verkocht / periode if periode > 0 else 0

    return round(gemiddelde_verkoop_per_dag * periode)

def automatisch_bestellen():
    voorraad = voorraadbeheer.laad_voorraad()
    for item in voorraad:
        if item.aantal < item.minimum_aantal:
            aantal_bestellen = voorspellen_bestelling(item.artikel_id)
            if aantal_bestellen > 0:
                bestelling = AutomatischeBestelling(item.artikel_id, aantal_bestellen, datetime.now())
                bestellingen = laad_automatische_bestellingen()
                bestellingen.append(bestelling)
                opslaan_automatische_bestellingen(bestellingen)
                print(f"🛒 Automatische bestelling geplaatst voor Artikel ID {item.artikel_id}: {aantal_bestellen} stuks.")

def toon_automatische_bestellingen():
    bestellingen = laad_automatische_bestellingen()
    if not bestellingen:
        print("ℹ️ Geen automatische bestellingen gevonden.")
        return
    print("🛒 Geregistreerde automatische bestellingen:")
    for b in bestellingen:
        print(f" - Artikel ID: {b.artikel_id} - Aantal te bestellen: {b.aantal_bestellen} - Besteldatum: {b.bestelling_datum.strftime('%Y-%m-%d')}")
