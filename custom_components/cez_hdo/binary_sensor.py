"""Binary sensor platform for CEZ HDO integration."""
from __future__ import annotations

import logging
from typing import Any

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
    
    async_add_entities([CezHdoBinarySensor(coordinator, config_entry)])


class CezHdoBinarySensor(CoordinatorEntity[CezHdoCoordinator], BinarySensorEntity):
    """Representation of a CEZ HDO binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_icon = "mdi:flash"

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
            "current_period": self.coordinator.data.get("current_period"),
            "next_switch": self.coordinator.data.get("next_switch"),
        }
        
        # Add today's switches
        switches = self.coordinator.data.get("today_switches", [])
        if switches:
            attrs["today_switches_count"] = len(switches)
            attrs["switches_today"] = [
                {
                    "time": switch["time"].strftime("%H:%M"),
                    "state": "low_tariff" if switch["state"] else "normal_tariff"
                }
                for switch in switches
            ]
        
        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
