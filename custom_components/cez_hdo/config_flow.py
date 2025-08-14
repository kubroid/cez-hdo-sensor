"""Config flow for CEZ HDO integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_EAN, CONF_SIGNAL, DEFAULT_SIGNAL, AVAILABLE_SIGNALS, DOMAIN
from .api import CezHdoApi

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EAN): str,
        vol.Optional(CONF_SIGNAL, default=DEFAULT_SIGNAL): vol.In(AVAILABLE_SIGNALS),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = CezHdoApi(data[CONF_EAN], data.get(CONF_SIGNAL, DEFAULT_SIGNAL))

    try:
        await api.async_get_data()
    except Exception as exc:
        _LOGGER.error("Cannot connect to CEZ API: %s", exc)
        raise CannotConnect from exc

    return {"title": f"CEZ HDO ({data[CONF_EAN]})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CEZ HDO."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidEan:
                errors["base"] = "invalid_ean"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_EAN])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidEan(HomeAssistantError):
    """Error to indicate there is invalid EAN."""
