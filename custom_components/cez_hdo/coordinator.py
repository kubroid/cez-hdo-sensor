"""Coordinator for CEZ HDO integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
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
        """Fetch data from API endpoint and compute current state."""
        try:
            # Get schedule data from API
            schedule_data = await self.api.async_get_data()
            if not schedule_data:
                _LOGGER.error("No data received from CEZ API - using error state")
                return self._get_error_state("No data received from CEZ API")

            # Check if we received error state from API
            if schedule_data.get("error_mode"):
                _LOGGER.warning("API returned error state: %s",
                              schedule_data.get("error_message", "Unknown error"))
                return schedule_data  # Return error state as-is

            # Compute current state based on schedule
            #now = datetime.now()
            #current_data = self._compute_current_state(schedule_data, now)

            return schedule_data

        except Exception as err:
            _LOGGER.error("Error in coordinator update: %s", err)
            # Return error state instead of raising exception
            return self._get_error_state(f"Error communicating with API: {err}")

    def _get_error_state(self, error_message: str) -> dict[str, Any]:
        """Return error state with low tariff for safety."""
        _LOGGER.warning("Returning error state with low tariff: %s", error_message)
        return {
            "is_low_tariff": True,  # Low tariff for safety
            "next_switch": None,
            "current_period": "low_tariff",
            "today_switches": [],
            "error_mode": True,
            "error_message": error_message
        }

    def _compute_current_state(self, schedule_data: dict[str, Any], now: datetime) -> dict[str, Any]:
        """Compute current HDO state based on schedule data."""
        # Start with the base data from API
        result = {
            "is_low_tariff": schedule_data.get("is_low_tariff", False),
            "next_switch": schedule_data.get("next_switch"),
            "current_period": schedule_data.get("current_period", "normal_tariff"),
            "today_switches": schedule_data.get("today_switches", [])
        }

        # If we have switches for today, recompute current state precisely
        switches = schedule_data.get("today_switches", [])
        if switches:
            current_state = False  # Default to normal tariff
            next_switch = None

            for switch in switches:
                switch_time = switch.get("time")
                if not switch_time:
                    continue

                # Ensure switch_time is datetime object
                if isinstance(switch_time, str):
                    try:
                        switch_time = datetime.fromisoformat(switch_time)
                    except ValueError:
                        continue

                if switch_time <= now:
                    current_state = switch["state"]
                elif next_switch is None:
                    next_switch = switch_time
                    break

            # Update result with computed values
            result["is_low_tariff"] = current_state
            result["next_switch"] = next_switch
            result["current_period"] = "low_tariff" if current_state else "normal_tariff"

            _LOGGER.debug(
                "HDO state computed: %s, Next switch: %s",
                "LOW TARIFF" if current_state else "NORMAL TARIFF",
                next_switch.strftime('%H:%M') if next_switch else "None"
            )

        return result

    async def async_shutdown(self) -> None:
        """Close the API session when shutting down."""
        await self.api.async_close()
