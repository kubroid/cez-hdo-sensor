#!/usr/bin/env python3
"""Extended test script for CEZ HDO API with detailed table output."""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Импортируем модули прямо
import aiohttp

# Константы для API
CEZ_API_URL = "https://dip.cezdistribuce.cz/irj/portal/anonymous/casy-spinani"
CEZ_API_ENDPOINT = "switch-times/signals"
CEZ_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "Origin": "https://dip.cezdistribuce.cz",
    "Connection": "keep-alive",
    "Referer": "https://dip.cezdistribuce.cz/irj/portal/anonymous/casy-spinani/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0"
}


class CezHdoApiExtended:
    """Extended CEZ HDO API client with detailed parsing."""

    def __init__(self, ean: str) -> None:
        """Initialize the API client."""
        self.ean = ean
        self._session: aiohttp.ClientSession | None = None

    async def async_get_data(self) -> Dict[str, Any]:
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
                    print(f"❌ API request failed with status {response.status}")
                    return {}
                
                raw_data = await response.json()
                parsed_data = self._parse_response(raw_data)
                
                # Return both raw and parsed data for detailed analysis
                return {
                    "raw_data": raw_data,
                    "parsed_data": parsed_data
                }
                
        except aiohttp.ClientError as err:
            print(f"❌ Error fetching data from CEZ API: {err}")
            return {}
        except json.JSONDecodeError as err:
            print(f"❌ Error decoding JSON response: {err}")
            return {}

    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the API response with detailed information."""
        result = {
            "is_low_tariff": False,
            "next_switch": None,
            "current_period": None,
            "today_switches": [],
            "tomorrow_switches": [],
            "all_switches": [],
            "statistics": {
                "total_switches": 0,
                "today_switches_count": 0,
                "tomorrow_switches_count": 0,
                "low_tariff_periods_today": 0,
                "total_low_tariff_duration_today": 0,
            }
        }
        
        try:
            # Extract all switch times
            switches = data.get("signals", [])
            now = datetime.now()
            today = now.date()
            tomorrow = today + timedelta(days=1)
            
            all_switches = []
            today_switches = []
            tomorrow_switches = []
            
            for switch in switches:
                try:
                    time_str = switch.get("time", "")
                    state = switch.get("state", False)
                    
                    # Handle different datetime formats
                    if "T" in time_str:
                        switch_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    else:
                        switch_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    
                    switch_info = {
                        "time": switch_time,
                        "state": state,
                        "date": switch_time.date(),
                        "hour": switch_time.hour,
                        "minute": switch_time.minute,
                        "is_past": switch_time <= now,
                        "time_until": switch_time - now if switch_time > now else None,
                        "time_since": now - switch_time if switch_time <= now else None
                    }
                    
                    all_switches.append(switch_info)
                    
                    if switch_time.date() == today:
                        today_switches.append(switch_info)
                    elif switch_time.date() == tomorrow:
                        tomorrow_switches.append(switch_info)
                        
                except (ValueError, TypeError) as err:
                    print(f"⚠️  Could not parse switch time '{time_str}': {err}")
                    continue
            
            # Sort switches by time
            all_switches.sort(key=lambda x: x["time"])
            today_switches.sort(key=lambda x: x["time"])
            tomorrow_switches.sort(key=lambda x: x["time"])
            
            result["all_switches"] = all_switches
            result["today_switches"] = today_switches
            result["tomorrow_switches"] = tomorrow_switches
            
            # Calculate statistics
            result["statistics"]["total_switches"] = len(all_switches)
            result["statistics"]["today_switches_count"] = len(today_switches)
            result["statistics"]["tomorrow_switches_count"] = len(tomorrow_switches)
            
            # Calculate low tariff periods for today
            low_tariff_periods = 0
            total_duration = 0
            current_period_start = None
            
            for i, switch in enumerate(today_switches):
                if switch["state"]:  # Start of low tariff
                    current_period_start = switch["time"]
                    low_tariff_periods += 1
                elif current_period_start:  # End of low tariff
                    duration = (switch["time"] - current_period_start).total_seconds() / 3600
                    total_duration += duration
                    current_period_start = None
            
            # If low tariff period extends beyond today
            if current_period_start and len(tomorrow_switches) > 0:
                for switch in tomorrow_switches:
                    if not switch["state"]:  # First OFF signal tomorrow
                        duration = (switch["time"] - current_period_start).total_seconds() / 3600
                        total_duration += duration
                        break
            
            result["statistics"]["low_tariff_periods_today"] = low_tariff_periods
            result["statistics"]["total_low_tariff_duration_today"] = round(total_duration, 2)
            
            # Determine current state and next switch
            current_state = False
            next_switch = None
            
            for switch in today_switches:
                if switch["time"] <= now:
                    current_state = switch["state"]
                elif next_switch is None:
                    next_switch = switch["time"]
                    break
            
            # If no more switches today, check tomorrow
            if next_switch is None and tomorrow_switches:
                next_switch = tomorrow_switches[0]["time"]
            
            result["is_low_tariff"] = current_state
            result["next_switch"] = next_switch
            result["current_period"] = "low_tariff" if current_state else "normal_tariff"
                
        except (KeyError, ValueError, TypeError) as err:
            print(f"❌ Error parsing API response: {err}")
        
        return result

    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None


def print_table_header(title: str, width: int = 80):
    """Print a formatted table header."""
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)


def print_switches_table(switches: List[Dict[str, Any]], title: str):
    """Print a formatted table of switches."""
    if not switches:
        print(f"\n📅 {title}: No switches scheduled")
        return
    
    print(f"\n📅 {title} ({len(switches)} switches):")
    print("┌─────────┬──────────┬───────────────┬──────────────┬────────────────┐")
    print("│  Time   │  Status  │     State     │   Duration   │    Relative    │")
    print("├─────────┼──────────┼───────────────┼──────────────┼────────────────┤")
    
    for i, switch in enumerate(switches):
        time_str = switch["time"].strftime("%H:%M")
        status = "✅ Past" if switch["is_past"] else "⏰ Future"
        state = "🟢 LOW TARIFF" if switch["state"] else "🔴 NORMAL"
        
        # Calculate duration to next switch
        duration = ""
        if i < len(switches) - 1:
            next_switch = switches[i + 1]
            delta = (next_switch["time"] - switch["time"]).total_seconds() / 3600
            duration = f"{delta:.1f}h"
        else:
            duration = "Until next day"
        
        # Relative time
        relative = ""
        if switch["time_until"]:
            total_seconds = int(switch["time_until"].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            relative = f"in {hours}h {minutes}m"
        elif switch["time_since"]:
            total_seconds = int(switch["time_since"].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            relative = f"{hours}h {minutes}m ago"
        
        print(f"│ {time_str:^7} │ {status:^8} │ {state:^13} │ {duration:^12} │ {relative:^14} │")
    
    print("└─────────┴──────────┴───────────────┴──────────────┴────────────────┘")


def print_statistics(stats: Dict[str, Any]):
    """Print statistics table."""
    print("\n📊 Statistics:")
    print("┌────────────────────────────────────┬──────────────┐")
    print("│            Metric                  │    Value     │")
    print("├────────────────────────────────────┼──────────────┤")
    print(f"│ Total switches in data             │ {stats['total_switches']:^12} │")
    print(f"│ Today's switches                   │ {stats['today_switches_count']:^12} │")
    print(f"│ Tomorrow's switches                │ {stats['tomorrow_switches_count']:^12} │")
    print(f"│ Low tariff periods today           │ {stats['low_tariff_periods_today']:^12} │")
    print(f"│ Total low tariff duration today    │ {stats['total_low_tariff_duration_today']:^10}h │")
    print("└────────────────────────────────────┴──────────────┘")


async def test_api_extended(ean: str):
    """Extended test the CEZ HDO API with detailed output."""
    print_table_header(f"🏠 CEZ HDO API Extended Test - EAN: {ean}")
    
    api = CezHdoApiExtended(ean)
    
    try:
        # Get data from API
        print("📡 Fetching data from CEZ API...")
        response = await api.async_get_data()
        
        if not response:
            print("❌ No data received from API")
            return False
        
        raw_data = response.get("raw_data", {})
        parsed_data = response.get("parsed_data", {})
        
        if not parsed_data:
            print("❌ Failed to parse API response")
            return False
        
        print("✅ API call successful!")
        
        # Current status
        print(f"\n🚦 Current Status:")
        print(f"   📊 Low tariff active: {'🟢 YES' if parsed_data.get('is_low_tariff') else '🔴 NO'}")
        print(f"   📅 Current period: {parsed_data.get('current_period', 'Unknown').replace('_', ' ').title()}")
        
        next_switch = parsed_data.get('next_switch')
        if next_switch:
            time_until = next_switch - datetime.now()
            hours = int(time_until.total_seconds() // 3600)
            minutes = int((time_until.total_seconds() % 3600) // 60)
            print(f"   ⏰ Next switch: {next_switch.strftime('%H:%M')} (in {hours}h {minutes}m)")
        else:
            print(f"   ⏰ Next switch: No more switches today")
        
        # Print detailed tables
        print_switches_table(parsed_data.get("today_switches", []), "Today's Schedule")
        print_switches_table(parsed_data.get("tomorrow_switches", []), "Tomorrow's Schedule")
        
        # Print statistics
        print_statistics(parsed_data.get("statistics", {}))
        
        # Raw API response info
        signals_count = len(raw_data.get("signals", []))
        print(f"\n🔍 Raw API Response Info:")
        print(f"   📊 Total signals in response: {signals_count}")
        print(f"   📅 Data covers multiple days: {'Yes' if signals_count > 0 else 'No'}")
        
        # Debug info
        print(f"\n🐛 Debug Info:")
        print(f"   🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📡 API endpoint: {CEZ_API_URL}?path={CEZ_API_ENDPOINT}")
        print(f"   🏷️  EAN code: {ean}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False
    
    finally:
        await api.async_close()


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python test_api_extended.py <EAN_CODE>")
        print("Example: python test_api_extended.py 859182400123456789")
        sys.exit(1)
    
    ean = sys.argv[1]
    
    try:
        success = asyncio.run(test_api_extended(ean))
        print("\n" + "="*80)
        if success:
            print("🎉 Test completed successfully!")
        else:
            print("💥 Test failed!")
        print("="*80)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
