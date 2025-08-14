#!/usr/bin/env python3
"""Test script for CEZ HDO API."""

import asyncio
import json
import sys
from datetime import datetime

# Импортируем модули прямо
import asyncio
import json
import aiohttp
from datetime import datetime, timedelta, time

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

class CezHdoApi:
    """CEZ HDO API client."""

    def __init__(self, ean: str, signal: str = "a3b4dp01") -> None:
        """Initialize the API client."""
        self.ean = ean
        self.signal = signal
        self._session: aiohttp.ClientSession | None = None

    async def async_get_data(self) -> dict:
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
                
        except aiohttp.ClientError as err:
            print(f"Error fetching data from CEZ API: {err}")
            return {}
        except json.JSONDecodeError as err:
            print(f"Error decoding JSON response: {err}")
            return {}

    def _parse_response(self, data: dict) -> dict:
        """Parse the API response."""
        result = {
            "is_low_tariff": False,
            "next_switch": None,
            "current_period": None,
            "today_switches": [],
            "raw_data": data
        }
        
        try:
            # Extract signals data
            signals_data = data.get("data", {}).get("signals", [])
            now = datetime.now()
            today = now.date()
            today_str = today.strftime("%d.%m.%Y")
            
            print(f"🔍 Looking for signal '{self.signal}' on date '{today_str}'")
            print(f"📡 Found {len(signals_data)} signal entries in response")
            
            # Find today's schedule for our signal
            today_schedule = None
            for signal_entry in signals_data:
                if (signal_entry.get("signal") == self.signal and 
                    signal_entry.get("datum") == today_str):
                    today_schedule = signal_entry.get("casy", "")
                    print(f"✅ Found schedule for {self.signal}: {today_schedule}")
                    break
            
            if not today_schedule:
                print(f"❌ No schedule found for signal '{self.signal}' on {today_str}")
                return result
            
            # Parse time ranges (format: "00:00-05:35;   06:30-08:55;   09:54-15:16")
            today_switches = []
            time_ranges = [r.strip() for r in today_schedule.split(';') if r.strip()]
            
            print(f"📅 Parsing {len(time_ranges)} time ranges")
            
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
                        
                        print(f"   ⏰ {start_str}-{end_str} → ON at {start_datetime.strftime('%H:%M')}, OFF at {end_datetime.strftime('%H:%M')}")
                        
                    except (ValueError, TypeError) as err:
                        print(f"⚠️  Could not parse time range '{time_range}': {err}")
                        continue
            
            # Sort switches by time
            today_switches.sort(key=lambda x: x["time"])
            result["today_switches"] = today_switches
            
            print(f"📊 Total switches created: {len(today_switches)}")
            
            # Determine current state and next switch
            current_state = False  # Default to normal tariff
            next_switch = None
            
            for switch in today_switches:
                if switch["time"] <= now:
                    current_state = switch["state"]
                    print(f"   🕐 Past switch at {switch['time'].strftime('%H:%M')}: {'LOW TARIFF' if switch['state'] else 'NORMAL'}")
                elif next_switch is None:
                    next_switch = switch["time"]
                    print(f"   ⏰ Next switch at {switch['time'].strftime('%H:%M')}: {'LOW TARIFF' if switch['state'] else 'NORMAL'}")
                    break
            
            result["is_low_tariff"] = current_state
            result["next_switch"] = next_switch
            result["current_period"] = "low_tariff" if current_state else "normal_tariff"
            
            print(f"🚦 Current state: {'LOW TARIFF' if current_state else 'NORMAL'}")
                
        except (KeyError, ValueError, TypeError) as err:
            print(f"❌ Error parsing API response: {err}")
        
        return result

    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None


async def test_api(ean: str, signal: str = "a3b4dp01"):
    """Test the CEZ HDO API."""
    print(f"Testing CEZ HDO API with EAN: {ean}, Signal: {signal}")
    
    api = CezHdoApi(ean, signal)
    
    try:
        data = await api.async_get_data()
        
        if not data:
            print("❌ No data received from API")
            return False
        
        print("✅ API call successful!")
        print("\n📊 Response data:")
        print(f"   Low tariff active: {data.get('is_low_tariff', 'Unknown')}")
        print(f"   Current period: {data.get('current_period', 'Unknown')}")
        print(f"   Next switch: {data.get('next_switch', 'Unknown')}")
        
        switches = data.get('today_switches', [])
        if switches:
            print(f"\n📅 Today's switches ({len(switches)}):")
            for switch in switches:
                time_str = switch['time'].strftime('%H:%M')
                state = "Low tariff" if switch['state'] else "Normal tariff"
                status = "✅" if switch['time'] <= datetime.now() else "⏰"
                print(f"   {status} {time_str} - {state}")
        else:
            print("\n📅 No switches scheduled for today")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        await api.async_close()


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <EAN_CODE> [SIGNAL]")
        print("Example: python test_api.py 859182400123456789")
        print("Example: python test_api.py 859182400123456789 a3b4dp01")
        print("Available signals: a3b4dp01, a3b4dp02, a3b4dp06")
        sys.exit(1)
    
    ean = sys.argv[1]
    signal = sys.argv[2] if len(sys.argv) > 2 else "a3b4dp01"
    
    try:
        success = asyncio.run(test_api(ean, signal))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
