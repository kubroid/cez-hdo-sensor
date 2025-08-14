#!/usr/bin/env python3
"""Test script for new CEZ HDO logic with minute updates and hour caching."""

import asyncio
import json
import logging
from datetime import datetime, timedelta, time
from typing import Any
import aiohttp

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Constants (copy from const.py)
CEZ_API_URL = "https://www.cezdistribuce.cz/webapi/reader"
CEZ_API_ENDPOINT = "/signals"
CEZ_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Home Assistant)",
}

class MockCezHdoApi:
    """Simplified version of CezHdoApi for testing."""

    def __init__(self, ean: str, signal: str = "a3b4dp01") -> None:
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
                    print(f"API request failed with status {response.status}")
                    return {}
                
                data = await response.json()
                return self._parse_response(data)
                
        except Exception as err:
            print(f"Error fetching data from CEZ API: {err}")
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
            now = datetime.now()
            today = now.date()
            
            print(f"Parsing CEZ API response for signal '{self.signal}'")
            
            # Navigate to signals data in new format
            datum_data = data.get("data", {}).get("datum", {})
            if not datum_data:
                print("No 'datum' data found in API response")
                return result
            
            casy_data = datum_data.get("casy", [])
            if not casy_data:
                print("No 'casy' data found in API response")
                return result
            
            print(f"Found {len(casy_data)} signal entries in casy data")
            
            # Find our signal in the casy array
            signal_data = None
            for signal_entry in casy_data:
                if signal_entry.get("signal") == self.signal:
                    signal_data = signal_entry
                    print(f"Found signal '{self.signal}' in response")
                    break
            
            if not signal_data:
                print(f"Signal '{self.signal}' not found in API response")
                print(f"Available signals: {[s.get('signal') for s in casy_data]}")
                return result
            
            # Get time ranges from signal data
            time_ranges = signal_data.get("casy", [])
            if not time_ranges:
                print(f"No time ranges found for signal '{self.signal}'")
                return result
            
            print(f"Found {len(time_ranges)} time ranges for signal '{self.signal}'")
            
            # Parse time ranges
            today_switches = []
            
            for time_range in time_ranges:
                start_time_str = time_range.get("od")
                end_time_str = time_range.get("do")
                
                if not start_time_str or not end_time_str:
                    print(f"Invalid time range: {time_range}")
                    continue
                
                try:
                    # Parse start time
                    start_hour, start_min = map(int, start_time_str.split(':'))
                    start_datetime = datetime.combine(today, time(start_hour, start_min))
                    
                    # Parse end time
                    end_hour, end_min = map(int, end_time_str.split(':'))
                    
                    # Handle midnight crossing
                    if end_hour == 24:
                        end_datetime = datetime.combine(today + timedelta(days=1), time(0, 0))
                    elif end_hour == 0 and start_hour > 12:
                        end_datetime = datetime.combine(today + timedelta(days=1), time(0, end_min))
                    else:
                        end_datetime = datetime.combine(today, time(end_hour, end_min))
                    
                    # Add switches
                    today_switches.append({
                        "time": start_datetime,
                        "state": True  # LOW TARIFF ON
                    })
                    today_switches.append({
                        "time": end_datetime,
                        "state": False  # LOW TARIFF OFF
                    })
                    
                    print(f"Time range {start_time_str}-{end_time_str}: ON at {start_datetime.strftime('%H:%M')}, OFF at {end_datetime.strftime('%H:%M')}")
                    
                except (ValueError, TypeError) as err:
                    print(f"Could not parse time range {start_time_str}-{end_time_str}: {err}")
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
            
            print(f"Current state: {'LOW TARIFF' if current_state else 'NORMAL TARIFF'}")
            if next_switch:
                print(f"Next switch: {next_switch.strftime('%H:%M')}")
                
        except Exception as err:
            print(f"Error parsing API response: {err}")
            print(f"Full API response: {json.dumps(data, indent=2, default=str)}")
        
        return result

    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None


class MockCoordinator:
    """Simplified coordinator for testing."""

    def __init__(self, ean: str, signal: str = "a3b4dp01") -> None:
        self.api = MockCezHdoApi(ean, signal)
        self.ean = ean
        self.signal = signal
        
        # Cached schedule data
        self._cached_schedule_data: dict[str, Any] = {}
        self._schedule_last_update: datetime | None = None
        self._schedule_update_interval = timedelta(hours=1)

    async def update_data(self) -> dict[str, Any]:
        """Update sensor state based on cached schedule or fetch new data."""
        now = datetime.now()
        
        # Check if we need to refresh schedule from API
        need_schedule_update = (
            not self._cached_schedule_data or 
            self._schedule_last_update is None or
            (now - self._schedule_last_update) >= self._schedule_update_interval
        )
        
        if need_schedule_update:
            print("🔄 Updating schedule from CEZ API")
            try:
                fresh_data = await self.api.async_get_data()
                if fresh_data:
                    self._cached_schedule_data = fresh_data
                    self._schedule_last_update = now
                    print("✅ Schedule updated successfully")
                else:
                    print("⚠️ No data received from CEZ API")
                    if not self._cached_schedule_data:
                        raise Exception("No data received from CEZ API and no cached data available")
            except Exception as err:
                print(f"❌ Error fetching schedule from API: {err}")
                if not self._cached_schedule_data:
                    raise
        else:
            print("📋 Using cached schedule data")
        
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
        current_state = False
        next_switch = None
        
        for switch in today_switches:
            switch_time = switch["time"]
            
            if switch_time <= now:
                current_state = switch["state"]
            elif next_switch is None:
                next_switch = switch_time
                break
        
        result = {
            "is_low_tariff": current_state,
            "next_switch": next_switch,
            "current_period": "low_tariff" if current_state else "normal_tariff",
            "today_switches": today_switches,
            "schedule_last_update": self._schedule_last_update,
        }
        
        print(f"📊 Current HDO state: {'LOW TARIFF' if current_state else 'NORMAL TARIFF'}")
        if next_switch:
            print(f"⏰ Next switch: {next_switch.strftime('%H:%M')}")
        
        return result

    async def close(self):
        """Close the API session."""
        await self.api.async_close()


async def test_new_logic():
    """Test the new CEZ HDO logic."""
    # Replace with your EAN
    ean = "123456789012345678"  # Example EAN
    signal = "a3b4dp01"
    
    print(f"🚀 Testing CEZ HDO logic for EAN: {ean}, Signal: {signal}")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    coordinator = MockCoordinator(ean, signal)
    
    try:
        # Simulate multiple updates (like the real integration would do)
        for i in range(3):
            print(f"\n📍 Update #{i+1}")
            print("-" * 30)
            
            data = await coordinator.update_data()
            
            print(f"Current period: {data['current_period']}")
            print(f"Is low tariff: {data['is_low_tariff']}")
            if data['next_switch']:
                print(f"Next switch: {data['next_switch'].strftime('%H:%M')}")
            if data['schedule_last_update']:
                age = datetime.now() - data['schedule_last_update']
                print(f"Schedule age: {int(age.total_seconds() / 60)} minutes")
            
            print(f"Today's switches: {len(data.get('today_switches', []))}")
            for switch in data.get('today_switches', []):
                print(f"  {switch['time'].strftime('%H:%M')} - {'LOW' if switch['state'] else 'NORMAL'}")
            
            # Simulate 30 second delay
            if i < 2:
                print("\n⏱️ Waiting 30 seconds...")
                await asyncio.sleep(5)  # Shortened for testing
        
    finally:
        await coordinator.close()
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    asyncio.run(test_new_logic())
