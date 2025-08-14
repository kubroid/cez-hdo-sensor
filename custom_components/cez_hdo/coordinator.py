"""Coordinator for CEZ HDO integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CezHdoApi
from .const import CONF_EAN, CONF_SIGNAL, DEFAULT_SIGNAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class CezHdoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching CEZ HDO data."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the coordinator."""
        self.api = CezHdoApi(config[CONF_EAN], config.get(CONF_SIGNAL, DEFAULT_SIGNAL))
        self.ean = config[CONF_EAN]
        self.signal = config.get(CONF_SIGNAL, DEFAULT_SIGNAL)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            data = await self.api.async_get_data()
            if not data:
                raise UpdateFailed("No data received from CEZ API")
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_shutdown(self) -> None:
        """Close the API session when shutting down."""
        await self.api.async_close()
