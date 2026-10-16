# ANWB Wasbeheer prijzen

Een kleine Home Assistant-integratie voor Slim Wasbeheer en het
Stroom-dashboard. De integratie leest elke 60 minuten de openbare ANWB
Energie-prijzen uit en bewaart de op dat moment gepubliceerde all-in stroom-
en gasprijzen, tot maximaal 72 uur. Er zijn geen accountgegevens, tokens of
wachtwoorden nodig.

De sensor `sensor.anwb_wasbeheer_all_in_price` bevat:

- de all-in prijs van het huidige uur in `€/kWh`;
- `hourly_prices`: alle op dat moment gepubliceerde komende uren met begin- en eindtijd, marktprijs en
  exacte all-in prijs;
- `forecast_start` en `forecast_end`.

Daarnaast levert de integratie een sensor **All-in gasprijs** met dezelfde
`hourly_prices`-voorspelling, in `€/m³`.

## Installatie

1. Voeg deze repository in HACS toe als **Integration**.
2. Download de integratie en herstart Home Assistant.
3. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen** en
   kies **ANWB Wasbeheer prijzen**.

De integratie leest uitsluitend publieke prijsinformatie. Hij schakelt geen
apparaten en stuurt geen gegevens naar ANWB.
