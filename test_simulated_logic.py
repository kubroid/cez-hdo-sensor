#!/usr/bin/env python3
"""Test script with simulated CEZ HDO data to verify logic."""

import asyncio
import json
from datetime import datetime, timedelta, time
from typing import Any

class SimulatedCezHdoApi:
    """Simulated API that returns test data."""

    def __init__(self, ean: str, signal: str = "a3b4dp01") -> None:
        self.ean = ean
        self.signal = signal

    async def async_get_data(self) -> dict[str, Any]:
        """Return simulated HDO data."""
        # Simulate current time-based schedule
        now = datetime.now()
        today = now.date()
        
        # Create test schedule: Low tariff 14:00-16:00 and 22:00-06:00
        test_data = {
            "data": {
                "datum": {
                    "casy": [
                        {
                            "signal": self.signal,
                            "casy": [
                                {"od": "14:00", "do": "16:00"},  # Afternoon low tariff
                                {"od": "22:00", "do": "06:00"}   # Night low tariff (crosses midnight)
                            ]
                        }
                    ]
                }
            }
        }
        
        return self._parse_response(test_data)

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
            
            print(f"📋 Parsing simulated data for signal '{self.signal}'")
            
            # Navigate to signals data in new format
            datum_data = data.get("data", {}).get("datum", {})
            casy_data = datum_data.get("casy", [])
            
            # Find our signal in the casy array
            signal_data = None
            for signal_entry in casy_data:
                if signal_entry.get("signal") == self.signal:
                    signal_data = signal_entry
                    print(f"✅ Found signal '{self.signal}' in response")
                    break
            
            if not signal_data:
                print(f"❌ Signal '{self.signal}' not found")
                return result
            
            # Get time ranges from signal data
            time_ranges = signal_data.get("casy", [])
            print(f"📊 Found {len(time_ranges)} time ranges")
            
            # Parse time ranges
            today_switches = []
            
            for time_range in time_ranges:
                start_time_str = time_range.get("od")
                end_time_str = time_range.get("do")
                
                print(f"⏰ Processing range: {start_time_str} - {end_time_str}")
                
                try:
                    # Parse start time
                    start_hour, start_min = map(int, start_time_str.split(':'))
                    start_datetime = datetime.combine(today, time(start_hour, start_min))
                    
                    # Parse end time
                    end_hour, end_min = map(int, end_time_str.split(':'))
                    
                    # Handle midnight crossing
                    if end_hour < start_hour or (end_hour == start_hour and end_min < start_min):
                        # Next day
                        end_datetime = datetime.combine(today + timedelta(days=1), time(end_hour, end_min))
                        print(f"  📅 Midnight crossing detected: end time is tomorrow")
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
                    
                    print(f"  ✅ ON at {start_datetime.strftime('%H:%M')}, OFF at {end_datetime.strftime('%d.%m %H:%M')}")
                    
                except (ValueError, TypeError) as err:
                    print(f"  ❌ Parse error: {err}")
                    continue
            
            # Sort switches by time
            today_switches.sort(key=lambda x: x["time"])
            result["today_switches"] = today_switches
            
            # Determine current state and next switch
            current_state = False  # Default to normal tariff
            next_switch = None
            
            print(f"\n🕐 Current time: {now.strftime('%H:%M')}")
            print("📋 Checking switches:")
            
            for switch in today_switches:
                switch_time = switch["time"]
                state_name = "LOW" if switch["state"] else "NORMAL"
                
                if switch_time <= now:
                    current_state = switch["state"]
                    print(f"  ✅ {switch_time.strftime('%d.%m %H:%M')} -> {state_name} (PAST - applied)")
                elif next_switch is None:
                    next_switch = switch_time
                    print(f"  ⏭️ {switch_time.strftime('%d.%m %H:%M')} -> {state_name} (NEXT)")
                    break
                else:
                    print(f"  ⏳ {switch_time.strftime('%d.%m %H:%M')} -> {state_name} (FUTURE)")
            
            result["is_low_tariff"] = current_state
            result["next_switch"] = next_switch
            result["current_period"] = "low_tariff" if current_state else "normal_tariff"
            
            print(f"\n🎯 Result: {'🟢 LOW TARIFF' if current_state else '🔴 NORMAL TARIFF'}")
            if next_switch:
                print(f"⏰ Next switch: {next_switch.strftime('%d.%m %H:%M')}")
                
        except Exception as err:
            print(f"❌ Error parsing response: {err}")
        
        return result

    async def async_close(self) -> None:
        """Close the session."""
        pass


class TestCoordinator:
    """Test coordinator."""

    def __init__(self, ean: str, signal: str = "a3b4dp01") -> None:
        self.api = SimulatedCezHdoApi(ean, signal)
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
            print("🔄 Updating schedule from API")
            fresh_data = await self.api.async_get_data()
            if fresh_data:
                self._cached_schedule_data = fresh_data
                self._schedule_last_update = now
                print("✅ Schedule updated successfully")
            else:
                print("⚠️ No data received from API")
        else:
            print("📋 Using cached schedule data")
            age_minutes = int((now - self._schedule_last_update).total_seconds() / 60)
            print(f"📊 Schedule age: {age_minutes} minutes")
        
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
        
        return result

    async def close(self):
        """Close the API session."""
        await self.api.async_close()


async def test_simulated_logic():
    """Test the new CEZ HDO logic with simulated data."""
    ean = "123456789012345678"
    signal = "a3b4dp01"
    
    print("🚀 Testing CEZ HDO Logic with Simulated Data")
    print("=" * 60)
    print(f"📱 EAN: {ean}")
    print(f"📡 Signal: {signal}")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📋 Test schedule: 14:00-16:00, 22:00-06:00 (low tariff)")
    print("=" * 60)
    
    coordinator = TestCoordinator(ean, signal)
    
    try:
        # Test multiple updates
        for i in range(4):
            print(f"\n📍 Update #{i+1}")
            print("-" * 40)
            
            data = await coordinator.update_data()
            
            print(f"\n📊 Results:")
            print(f"  Current period: {data['current_period']}")
            print(f"  Is low tariff: {'🟢 YES' if data['is_low_tariff'] else '🔴 NO'}")
            
            if data['next_switch']:
                print(f"  Next switch: {data['next_switch'].strftime('%d.%m %H:%M')}")
            else:
                print(f"  Next switch: None (end of day)")
                
            if data['schedule_last_update']:
                age = datetime.now() - data['schedule_last_update']
                print(f"  Schedule age: {int(age.total_seconds() / 60)} minutes")
            
            switches = data.get('today_switches', [])
            print(f"  Today's switches: {len(switches)}")
            for j, switch in enumerate(switches):
                state_emoji = "🟢" if switch['state'] else "🔴"
                state_name = "LOW" if switch['state'] else "NORMAL"
                print(f"    {j+1}. {switch['time'].strftime('%d.%m %H:%M')} {state_emoji} {state_name}")
            
            # Simulate 1 minute delay for testing caching
            if i < 3:
                print(f"\n⏱️ Waiting...")
                await asyncio.sleep(2)  # Shortened for testing
        
    finally:
        await coordinator.close()
    
    print(f"\n✅ Test completed!")
    print("\n📋 Summary:")
    print("- Schedule is cached for 1 hour")
    print("- Sensor state is recalculated every minute")
    print("- API calls are minimized")
    print("- Real-time HDO switching without delays")


if __name__ == "__main__":
    asyncio.run(test_simulated_logic())
