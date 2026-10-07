"""Sensors for ANWB Wasbeheer prijzen."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AnwbWasbeheerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ANWB all-in price sensor."""
    coordinator: AnwbWasbeheerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AnwbAllInPriceSensor(coordinator, entry)])


class AnwbAllInPriceSensor(CoordinatorEntity[AnwbWasbeheerCoordinator], SensorEntity):
    """Current exact ANWB all-in price with a 72-hour forecast attribute."""

    _attr_has_entity_name = True
    _attr_name = "All-in elektriciteitsprijs"
    _attr_native_unit_of_measurement = "€/kWh"
    _attr_icon = "mdi:transmission-tower"

    def __init__(self, coordinator: AnwbWasbeheerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_all_in_price"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="ANWB Wasbeheer prijzen",
            manufacturer="ANWB Energie",
            model="Publieke uurprijzen",
        )

    @property
    def native_value(self) -> float | None:
        """Return the all-in price for the present hour."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data[0]["all_in_price"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose a compact, machine-readable 72-hour forecast."""
        return {
            "forecast_start": self.coordinator.forecast_start.isoformat()
            if self.coordinator.forecast_start
            else None,
            "forecast_end": self.coordinator.forecast_end.isoformat()
            if self.coordinator.forecast_end
            else None,
            "hourly_prices": self.coordinator.data or [],
            "source": "ANWB Energie publieke all-in uurprijzen",
        }
