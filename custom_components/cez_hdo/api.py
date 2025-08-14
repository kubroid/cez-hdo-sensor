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
        """Parse the API response."""
        result = {
            "is_low_tariff": False,
            "next_switch": None,
            "current_period": None,
            "today_switches": []
        }
        
        try:
            # Extract signals data
            signals_data = data.get("data", {}).get("signals", [])
            now = datetime.now()
            today = now.date()
            today_str = today.strftime("%d.%m.%Y")
            
            _LOGGER.debug("Looking for signal '%s' on date '%s'", self.signal, today_str)
            _LOGGER.debug("Found %d signal entries in response", len(signals_data))
            
            # Find today's schedule for our signal
            today_schedule = None
            for signal_entry in signals_data:
                if (signal_entry.get("signal") == self.signal and 
                    signal_entry.get("datum") == today_str):
                    today_schedule = signal_entry.get("casy", "")
                    _LOGGER.debug("Found schedule for %s: %s", self.signal, today_schedule)
                    break
            
            if not today_schedule:
                _LOGGER.warning("No schedule found for signal '%s' on %s", self.signal, today_str)
                return result
            
            # Parse time ranges (format: "00:00-05:35;   06:30-08:55;   09:54-15:16")
            today_switches = []
            time_ranges = [r.strip() for r in today_schedule.split(';') if r.strip()]
            
            _LOGGER.debug("Parsing %d time ranges", len(time_ranges))
            
            for time_range in time_ranges:
                if '-' in time_range:
                    try:
                        start_str, end_str = time_range.split('-')
                        start_str = start_str.strip()
                        end_str = end_str.strip()
                        
                        # Parse start time
                        start_hour, start_min = map(int, start_str.split(':'))
                        start_datetime = datetime.combine(today, time(start_hour, start_min))
                        
                        # Parse end time
                        end_hour, end_min = map(int, end_str.split(':'))
                        
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
                                    start_str, end_str, 
                                    start_datetime.strftime('%H:%M'), 
                                    end_datetime.strftime('%H:%M'))
                        
                    except (ValueError, TypeError) as err:
                        _LOGGER.warning("Could not parse time range '%s': %s", time_range, err)
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
        
        return result

    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None
