"""Binary sensor platform for CEZ HDO integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from datetime import datetime

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_EAN, DOMAIN
from .coordinator import CezHdoCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CEZ HDO binary sensor based on a config entry."""
    coordinator: CezHdoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create both main HDO sensor and error sensor
    async_add_entities([
        CezHdoBinarySensor(coordinator, config_entry),
        CezHdoErrorSensor(coordinator, config_entry)
    ])


class CezHdoBinarySensor(CoordinatorEntity[CezHdoCoordinator], BinarySensorEntity):
    """Representation of a CEZ HDO binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.POWER

    def __init__(
        self,
        coordinator: CezHdoCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)

        self._attr_unique_id = f"cez_hdo_{coordinator.ean}"
        self._attr_name = f"CEZ HDO {coordinator.ean}"
        self._ean = coordinator.ean

        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.ean)},
            "name": f"CEZ HDO {coordinator.ean}",
            "manufacturer": "ČEZ Distribuce",
            "model": "HDO Signal",
            "entry_type": "service",
            "suggested_area": "Utility",
        }

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        if self.is_on:
            return "mdi:flash"  # Low tariff active
        else:
            return "mdi:flash-outline"  # Normal tariff

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on (low tariff is active)."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("is_low_tariff", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data is None:
            return {}

        attrs = {
            "ean": self._ean,
            "signal": self.coordinator.signal,
            "current_period": self.coordinator.data.get("current_period"),
            "next_switch": self.coordinator.data.get("next_switch"),
        }

        # Check for error mode
        if self.coordinator.data.get("error_mode"):
            attrs["error_mode"] = True
            attrs["error_message"] = self.coordinator.data.get("error_message", "Unknown error")
            attrs["safety_mode"] = "low_tariff_activated"
        else:
            attrs["error_mode"] = False

        # Add schedule update information
        schedule_update = self.coordinator.data.get("schedule_last_update")
        if schedule_update:
            attrs["schedule_last_update"] = schedule_update.strftime("%Y-%m-%d %H:%M:%S")
            # Calculate age in minutes
            now = datetime.now()
            attrs["schedule_age_minutes"] = int((now - schedule_update).total_seconds() / 60)

        # Add today's switches
        switches = self.coordinator.data.get("today_switches", [])
        if switches:
            attrs["today_switches_count"] = len(switches)
            attrs["switches_today"] = [
                {
                    "time": switch["time"].strftime("%H:%M") if hasattr(switch["time"], "strftime") else str(switch["time"]),
                    "state": "low_tariff" if switch["state"] else "normal_tariff"
                }
                for switch in switches
            ]

        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Entity is always available, even in error mode
        return True

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        if self.is_on:
            return "mdi:flash"  # Low tariff active
        else:
            return "mdi:flash-outline"  # Normal tariff


class CezHdoErrorSensor(CoordinatorEntity[CezHdoCoordinator], BinarySensorEntity):
    """Representation of a CEZ HDO error sensor."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:alert-circle"

    def __init__(
        self,
        coordinator: CezHdoCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the error sensor."""
        super().__init__(coordinator)

        self._attr_unique_id = f"cez_hdo_error_{coordinator.ean}"
        self._attr_name = f"CEZ HDO Error {coordinator.ean}"
        self._ean = coordinator.ean

        # Device info - same device as main sensor
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.ean)},
            "name": f"CEZ HDO {coordinator.ean}",
            "manufacturer": "ČEZ Distribuce",
            "model": "HDO Signal",
            "entry_type": "service",
            "suggested_area": "Utility",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if there is an error."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("error_mode", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data is None:
            return {}

        attrs = {
            "ean": self._ean,
            "signal": self.coordinator.signal,
        }

        # Add error information if available
        if self.coordinator.data.get("error_mode"):
            attrs["error_message"] = self.coordinator.data.get("error_message", "Unknown error")
            attrs["safety_mode"] = "low_tariff_activated"
            attrs["last_error_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Error sensor is always available to report errors
        return True
