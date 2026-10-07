"""Config flow for ANWB Wasbeheer prijzen."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class AnwbWasbeheerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow without credentials."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Create the single public-price entry."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="ANWB Wasbeheer prijzen", data={})
