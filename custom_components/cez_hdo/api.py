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
        self.next_switch = None
        self.cached = None

    async def async_get_data(self) -> dict[str, Any]:
        """Get HDO data from CEZ API."""
        now = datetime.now()
        if self.next_switch is None or self.cached is None or self.next_switch < now:
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
                        return self._get_error_state("API request failed")

                    data = await response.json()
                    response = self._parse_response(data)
                    self.next_switch = response.get('next_switch')
                    self.cached = response
            except aiohttp.ClientError as err:
                _LOGGER.error("Error fetching data from CEZ API: %s", err)
                return self._get_error_state(f"Network error: {err}")
            except json.JSONDecodeError as err:
                _LOGGER.error("Error decoding JSON response: %s", err)
                return self._get_error_state(f"JSON decode error: {err}")
            except Exception as err:
                _LOGGER.error("Unexpected error: %s", err)
                return self._get_error_state(f"Unexpected error: {err}")
        return self.cached


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

    def _parse_response(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse the API response for real CEZ format."""
        result = {
            "is_low_tariff": False,
            "next_switch": None,
            "current_period": "normal_tariff",
            "today_switches": []
        }

        try:
            now = datetime.now()
            today = now.date()
            today_str = today.strftime("%d.%m.%Y")

            _LOGGER.debug("Parsing CEZ API response for signal '%s', today: %s", self.signal, today_str)

            # Real CEZ API format: data.signals[] with signal, den, datum, casy
            signals_data = data.get("data", {}).get("signals", [])
            if not signals_data:
                _LOGGER.warning("No 'signals' data found in API response")
                return result

            _LOGGER.debug("Found %d signal entries", len(signals_data))

            # Find today's data for our signal
            today_signal_data = None
            for signal_entry in signals_data:
                if (signal_entry.get("signal") == self.signal and
                    signal_entry.get("datum") == today_str):
                    today_signal_data = signal_entry
                    _LOGGER.debug("Found today's data for signal '%s'", self.signal)
                    break

            if not today_signal_data:
                _LOGGER.warning("Today's data for signal '%s' not found", self.signal)
                return self._get_error_state(f"Signal '{self.signal}' not found in API response")

            # Parse time ranges from casy string
            casy_string = today_signal_data.get("casy", "")
            if not casy_string:
                _LOGGER.warning("No time ranges found for signal '%s'", self.signal)
                return self._get_error_state(f"No schedule data for signal '{self.signal}'")

            _LOGGER.debug("Raw casy string: '%s'", casy_string)

            # Parse time ranges: "00:00-05:35; 06:30-08:55; ..."
            today_switches = []

            # Split by semicolon and clean up
            time_ranges = [r.strip() for r in casy_string.split(';') if r.strip()]

            for time_range in time_ranges:
                if '-' not in time_range:
                    continue

                try:
                    start_time_str, end_time_str = time_range.split('-', 1)
                    start_time_str = start_time_str.strip()
                    end_time_str = end_time_str.strip()

                    # Parse start time
                    start_hour, start_min = map(int, start_time_str.split(':'))
                    start_datetime = datetime.combine(today, time(start_hour, start_min))

                    # Parse end time - handle 24:00 as next day 00:00
                    if end_time_str == "24:00":
                        end_datetime = datetime.combine(today + timedelta(days=1), time(0, 0))
                    else:
                        end_hour, end_min = map(int, end_time_str.split(':'))
                        if end_hour == 24:
                            end_datetime = datetime.combine(today + timedelta(days=1), time(0, 0))
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

            _LOGGER.debug("Current state: %s, Next switch: %s",
                         "LOW TARIFF" if current_state else "NORMAL TARIFF",
                         next_switch.strftime('%H:%M') if next_switch else "None")

        except (KeyError, ValueError, TypeError) as err:
            _LOGGER.error("Error parsing API response: %s", err)
            _LOGGER.debug("Full API response: %s", data)
            return self._get_error_state(f"Failed to parse API response: {err}")
        except Exception as err:
            _LOGGER.error("Unexpected error during parsing: %s", err)
            return self._get_error_state(f"Unexpected parsing error: {err}")

        return result

    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None
