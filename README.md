# ANWB Wasbeheer prijzen

Een kleine Home Assistant-integratie voor Slim Wasbeheer. De integratie leest
elke 60 minuten de openbare ANWB Energie-prijzen uit en bewaart 72 uur aan
all-in elektriciteitsprijzen. Er zijn geen accountgegevens, tokens of
wachtwoorden nodig.

De sensor `sensor.anwb_wasbeheer_all_in_price` bevat:

- de all-in prijs van het huidige uur in `€/kWh`;
- `hourly_prices`: de komende 72 uur met begin- en eindtijd, marktprijs en
  exacte all-in prijs;
- `forecast_start` en `forecast_end`.

## Installatie

1. Voeg deze repository in HACS toe als **Integration**.
2. Download de integratie en herstart Home Assistant.
3. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen** en
   kies **ANWB Wasbeheer prijzen**.

De integratie leest uitsluitend publieke prijsinformatie. Hij schakelt geen
apparaten en stuurt geen gegevens naar ANWB.
