"""Coordinator that reads the public ANWB Energy price feed."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL_BASE, DOMAIN, ENERGY_TYPES, FORECAST_HOURS, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AnwbWasbeheerCoordinator(DataUpdateCoordinator[dict[str, list[dict[str, Any]]]]):
    """Fetch ANWB all-in electricity and gas prices from one public API."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.forecast_start: dict[str, datetime | None] = {}
        self.forecast_end: dict[str, datetime | None] = {}

    async def _async_update_data(self) -> dict[str, list[dict[str, Any]]]:
        """Retrieve the published all-in prices for both energy types."""
        prices = {"electricity": await self._async_fetch_prices("electricity")}
        try:
            prices["gas"] = await self._async_fetch_prices("gas")
        except UpdateFailed as err:
            # A missing gas feed must not take the electricity-price source
            # (used by the laundry planner) offline.
            _LOGGER.warning("ANWB-gasprijzen niet beschikbaar: %s", err)
            prices["gas"] = []
        return prices

    async def _async_fetch_prices(self, energy_type: str) -> list[dict[str, Any]]:
        """Retrieve and validate the 72-hour ANWB feed for one energy type."""
        if energy_type not in ENERGY_TYPES:
            raise ValueError(f"Onbekend energietype: {energy_type}")
        start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=FORECAST_HOURS)
        params = {
            "startDate": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "endDate": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "interval": "HOUR",
        }
        headers = {
            "Accept": "application/json",
            "Accept-Language": "nl,en;q=0.9",
            "Origin": "https://www.anwb.nl",
            "Referer": "https://www.anwb.nl/",
            "User-Agent": "Mozilla/5.0 (Home Assistant; ANWB Wasbeheer)",
        }
        try:
            async with async_get_clientsession(self.hass).get(
                f"{API_URL_BASE}/{energy_type}", params=params, headers=headers, timeout=30
            ) as response:
                response.raise_for_status()
                payload = await response.json()
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"ANWB-{energy_type}prijzen niet beschikbaar: {err}") from err

        rows: list[dict[str, Any]] = []
        for row in payload.get("data", []):
            values = row.get("values", {})
            try:
                begins = datetime.fromisoformat(str(row["date"]).replace("Z", "+00:00"))
                market_cents = float(values["marktprijs"])
                all_in_cents = float(values["allInPrijs"])
            except (KeyError, TypeError, ValueError):
                continue
            rows.append(
                {
                    "start": begins.isoformat(),
                    "end": (begins + timedelta(hours=1)).isoformat(),
                    "market_price": round(market_cents / 100, 5),
                    "all_in_price": round(all_in_cents / 100, 5),
                }
            )

        # ANWB publishes prices gradually. Near the end of the published
        # window there can legitimately be fewer than 24 hours available.
        # Keep those exact hours available; later dashboard slots remain
        # visibly unknown until ANWB publishes them.
        if not rows:
            raise UpdateFailed(f"ANWB stuurde geen bruikbare {energy_type}prijzen")

        self.forecast_start[energy_type] = datetime.fromisoformat(rows[0]["start"])
        self.forecast_end[energy_type] = datetime.fromisoformat(rows[-1]["end"])
        return rows
