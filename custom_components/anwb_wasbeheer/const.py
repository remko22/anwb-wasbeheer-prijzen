"""Constants for ANWB Wasbeheer prijzen."""

from datetime import timedelta
from typing import Final

DOMAIN: Final = "anwb_wasbeheer"
PLATFORMS: Final = ["sensor"]
UPDATE_INTERVAL: Final = timedelta(minutes=60)
FORECAST_HOURS: Final = 72
API_URL: Final = "https://api.anwb.nl/energy/energy-services/v2/tarieven/electricity"
