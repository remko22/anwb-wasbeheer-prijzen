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
    """Set up the ANWB all-in electricity and gas price sensors."""
    coordinator: AnwbWasbeheerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            AnwbAllInPriceSensor(coordinator, entry, "electricity"),
            AnwbAllInPriceSensor(coordinator, entry, "gas"),
        ]
    )


class AnwbAllInPriceSensor(CoordinatorEntity[AnwbWasbeheerCoordinator], SensorEntity):
    """Current ANWB all-in price with a 72-hour forecast attribute."""

    _attr_has_entity_name = True
    def __init__(
        self,
        coordinator: AnwbWasbeheerCoordinator,
        entry: ConfigEntry,
        energy_type: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._energy_type = energy_type
        # Keep the original electricity unique ID so its entity ID remains
        # stable for Slim Wasbeheer and existing dashboards.
        self._attr_unique_id = (
            f"{entry.entry_id}_all_in_price"
            if energy_type == "electricity"
            else f"{entry.entry_id}_all_in_gas_price"
        )
        self._attr_name = (
            "All-in elektriciteitsprijs"
            if energy_type == "electricity"
            else "All-in gasprijs"
        )
        self._attr_native_unit_of_measurement = (
            "€/kWh" if energy_type == "electricity" else "€/m³"
        )
        self._attr_icon = (
            "mdi:transmission-tower" if energy_type == "electricity" else "mdi:fire"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="ANWB Wasbeheer prijzen",
            manufacturer="ANWB Energie",
            model="Publieke stroom- en gasprijzen",
        )

    @property
    def native_value(self) -> float | None:
        """Return the all-in price for the present hour."""
        if not self.coordinator.data or not self.coordinator.data.get(self._energy_type):
            return None
        return self.coordinator.data[self._energy_type][0]["all_in_price"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose a compact, machine-readable 72-hour forecast."""
        return {
            "forecast_start": self.coordinator.forecast_start.get(self._energy_type).isoformat()
            if self.coordinator.forecast_start.get(self._energy_type)
            else None,
            "forecast_end": self.coordinator.forecast_end.get(self._energy_type).isoformat()
            if self.coordinator.forecast_end.get(self._energy_type)
            else None,
            "hourly_prices": (self.coordinator.data or {}).get(self._energy_type, []),
            "source": "ANWB Energie publieke all-in uurprijzen",
            "energy_type": self._energy_type,
        }
