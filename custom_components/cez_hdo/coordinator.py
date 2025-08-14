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
    """Class to manage fetching CEZ HDO data with smart caching."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the coordinator."""
        self.api = CezHdoApi(config[CONF_EAN], config.get(CONF_SIGNAL, DEFAULT_SIGNAL))
        self.ean = config[CONF_EAN]
        self.signal = config.get(CONF_SIGNAL, DEFAULT_SIGNAL)
        
        # Cached schedule data
        self._cached_schedule_data: dict[str, Any] = {}
        self._schedule_last_update: datetime | None = None
        self._schedule_update_interval = timedelta(hours=1)  # Update schedule every hour
        
        # Update sensor state every minute
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),  # Check state every minute
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update sensor state based on cached schedule or fetch new data."""
        now = datetime.now()
        
        # Check if we need to refresh schedule from API
        need_schedule_update = (
            not self._cached_schedule_data or 
            self._schedule_last_update is None or
            (now - self._schedule_last_update) >= self._schedule_update_interval
        )
        
        if need_schedule_update:
            _LOGGER.debug("Updating schedule from CEZ API")
            try:
                # Fetch fresh schedule data from API
                fresh_data = await self.api.async_get_data()
                if fresh_data:
                    self._cached_schedule_data = fresh_data
                    self._schedule_last_update = now
                    _LOGGER.debug("Schedule updated successfully")
                else:
                    _LOGGER.warning("No data received from CEZ API")
                    if not self._cached_schedule_data:
                        raise UpdateFailed("No data received from CEZ API and no cached data available")
            except Exception as err:
                _LOGGER.error("Error fetching schedule from API: %s", err)
                if not self._cached_schedule_data:
                    raise UpdateFailed(f"Error communicating with API: {err}") from err
        
        # Calculate current state based on cached schedule
        return self._calculate_current_state()

    def _calculate_current_state(self) -> dict[str, Any]:
        """Calculate current HDO state based on cached schedule."""
        if not self._cached_schedule_data:
            return {
                "is_low_tariff": False,
                "next_switch": None,
                "current_period": "normal_tariff",
                "today_switches": [],
                "schedule_last_update": self._schedule_last_update,
            }
        
        now = datetime.now()
        today_switches = self._cached_schedule_data.get("today_switches", [])
        
        # Determine current state based on switches
        current_state = False  # Default to normal tariff
        next_switch = None
        
        for switch in today_switches:
            switch_time = switch["time"]
            if isinstance(switch_time, str):
                # If time is stored as string, parse it
                switch_time = datetime.fromisoformat(switch_time)
            
            if switch_time <= now:
                current_state = switch["state"]
            elif next_switch is None:
                next_switch = switch_time
                break
        
        # If no next switch found today, check if we need to look at tomorrow
        if next_switch is None and today_switches:
            # Look for first switch tomorrow (if any)
            tomorrow = now.date() + timedelta(days=1)
            # For now, just set next_switch to None - we could extend this later
        
        result = {
            "is_low_tariff": current_state,
            "next_switch": next_switch,
            "current_period": "low_tariff" if current_state else "normal_tariff",
            "today_switches": today_switches,
            "schedule_last_update": self._schedule_last_update,
        }
        
        _LOGGER.debug(
            "Current HDO state: %s, Next switch: %s", 
            "LOW TARIFF" if current_state else "NORMAL TARIFF",
            next_switch.strftime('%H:%M') if next_switch else "None"
        )
        
        return result

    async def async_shutdown(self) -> None:
        """Close the API session when shutting down."""
        await self.api.async_close()
