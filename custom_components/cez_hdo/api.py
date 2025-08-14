"""API for CEZ HDO."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta, time
from typing import Any

import aiohttp

from .const import CEZ_API_ENDPOINT, CEZ_API_URL, CEZ_HEADERS

_LOGGER = logging.getLogger(__name__)


class CezHdoApi:
    """CEZ HDO API client."""

    def __init__(self, ean: str, signal: str = "a3b4dp01") -> None:
        """Initialize the API client."""
        self.ean = ean
        self.signal = signal
        self._session: aiohttp.ClientSession | None = None

    async def async_get_data(self) -> dict[str, Any]:
        """Get HDO data from CEZ API."""
        url = f"{CEZ_API_URL}?path={CEZ_API_ENDPOINT}"
        payload = {"ean": self.ean}
        
        if self._session is None:
            self._session = aiohttp.ClientSession()
        
        try:
            async with self._session.post(
                url,
                headers=CEZ_HEADERS,
                data=json.dumps(payload),
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    _LOGGER.error("API request failed with status %d", response.status)
                    return {}
                
                data = await response.json()
                return self._parse_response(data)
                
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching data from CEZ API: %s", err)
            return {}
        except json.JSONDecodeError as err:
            _LOGGER.error("Error decoding JSON response: %s", err)
            return {}

    def _parse_response(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse the API response for new CEZ format."""
        result = {
            "is_low_tariff": False,
            "next_switch": None,
            "current_period": None,
            "today_switches": []
        }
        
        try:
            # New CEZ API format: data.datum.casy[signal].casy
            now = datetime.now()
            today = now.date()
            
            _LOGGER.debug("Parsing CEZ API response for signal '%s'", self.signal)
            
            # Navigate to signals data in new format
            datum_data = data.get("data", {}).get("datum", {})
            if not datum_data:
                _LOGGER.warning("No 'datum' data found in API response")
                return result
            
            casy_data = datum_data.get("casy", [])
            if not casy_data:
                _LOGGER.warning("No 'casy' data found in API response")
                return result
            
            _LOGGER.debug("Found %d signal entries in casy data", len(casy_data))
            
            # Find our signal in the casy array
            signal_data = None
            for signal_entry in casy_data:
                if signal_entry.get("signal") == self.signal:
                    signal_data = signal_entry
                    _LOGGER.debug("Found signal '%s' in response", self.signal)
                    break
            
            if not signal_data:
                _LOGGER.warning("Signal '%s' not found in API response", self.signal)
                return result
            
            # Get time ranges from signal data
            time_ranges = signal_data.get("casy", [])
            if not time_ranges:
                _LOGGER.warning("No time ranges found for signal '%s'", self.signal)
                return result
            
            _LOGGER.debug("Found %d time ranges for signal '%s'", len(time_ranges), self.signal)
            
            # Parse time ranges
            today_switches = []
            
            for time_range in time_ranges:
                start_time_str = time_range.get("od")  # "from" time
                end_time_str = time_range.get("do")    # "to" time
                
                if not start_time_str or not end_time_str:
                    _LOGGER.warning("Invalid time range: %s", time_range)
                    continue
                
                try:
                    # Parse start time
                    start_hour, start_min = map(int, start_time_str.split(':'))
                    start_datetime = datetime.combine(today, time(start_hour, start_min))
                    
                    # Parse end time
                    end_hour, end_min = map(int, end_time_str.split(':'))
                    
                    # Handle midnight crossing (24:00 becomes next day 00:00)
                    if end_hour == 24:
                        end_datetime = datetime.combine(today + timedelta(days=1), time(0, 0))
                    elif end_hour == 0 and start_hour > 12:  # Midnight crossing
                        end_datetime = datetime.combine(today + timedelta(days=1), time(0, end_min))
                    else:
                        end_datetime = datetime.combine(today, time(end_hour, end_min))
                    
                    # Add switches: ON at start, OFF at end
                    today_switches.append({
                        "time": start_datetime,
                        "state": True  # LOW TARIFF ON
                    })
                    today_switches.append({
                        "time": end_datetime,
                        "state": False  # LOW TARIFF OFF
                    })
                    
                    _LOGGER.debug("Time range %s-%s: ON at %s, OFF at %s", 
                                start_time_str, end_time_str, 
                                start_datetime.strftime('%H:%M'), 
                                end_datetime.strftime('%H:%M'))
                    
                except (ValueError, TypeError) as err:
                    _LOGGER.warning("Could not parse time range %s-%s: %s", 
                                  start_time_str, end_time_str, err)
                    continue
            
            # Sort switches by time
            today_switches.sort(key=lambda x: x["time"])
            result["today_switches"] = today_switches
            
            # Determine current state and next switch
            current_state = False  # Default to normal tariff
            next_switch = None
            
            for switch in today_switches:
                if switch["time"] <= now:
                    current_state = switch["state"]
                elif next_switch is None:
                    next_switch = switch["time"]
                    break
            
            result["is_low_tariff"] = current_state
            result["next_switch"] = next_switch
            result["current_period"] = "low_tariff" if current_state else "normal_tariff"
            
            _LOGGER.debug("Current state: %s", "LOW TARIFF" if current_state else "NORMAL")
                
        except (KeyError, ValueError, TypeError) as err:
            _LOGGER.error("Error parsing API response: %s", err)
            _LOGGER.debug("Full API response: %s", data)
        
        return result

    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None
