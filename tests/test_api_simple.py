#!/usr/bin/env python3
"""Simple table test for CEZ HDO API with real data."""

import asyncio
import json
import sys
from datetime import datetime, timedelta
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


async def get_cez_data(ean: str):
    """Get data from CEZ API."""
    url = f"{CEZ_API_URL}?path={CEZ_API_ENDPOINT}"
    payload = {"ean": ean}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url,
                headers=CEZ_HEADERS,
                data=json.dumps(payload),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    print(f"❌ API request failed with status {response.status}")
                    return None
                
                return await response.json()
                
        except Exception as err:
            print(f"❌ Error fetching data: {err}")
            return None


def print_simple_table(data):
    """Print a simple table of HDO switches."""
    print(f"\n🔍 Raw API Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    if not data or "signals" not in data:
        print("❌ No 'signals' key in response data")
        if data:
            print(f"📋 Available keys: {list(data.keys())}")
        return
    
    signals = data["signals"]
    now = datetime.now()
    today = now.date()
    
    print(f"\n📊 HDO Schedule Analysis")
    print(f"🕐 Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📡 Total signals received: {len(signals)}")
    
    # Parse switches
    switches = []
    for signal in signals:
        try:
            time_str = signal.get("time", "")
            state = signal.get("state", False)
            
            if "T" in time_str:
                switch_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            else:
                switch_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            
            switches.append({
                "time": switch_time,
                "state": state,
                "date": switch_time.date(),
                "is_today": switch_time.date() == today,
                "is_past": switch_time <= now
            })
        except Exception as e:
            print(f"⚠️  Could not parse time '{time_str}': {e}")
    
    switches.sort(key=lambda x: x["time"])
    
    # Today's switches
    today_switches = [s for s in switches if s["is_today"]]
    
    if today_switches:
        print(f"\n📅 Today's HDO Schedule ({len(today_switches)} switches):")
        print("┌──────────────────────┬───────────────┬──────────┐")
        print("│        Time          │     State     │  Status  │")
        print("├──────────────────────┼───────────────┼──────────┤")
        
        for switch in today_switches:
            time_str = switch["time"].strftime("%H:%M")
            date_str = switch["time"].strftime("%Y-%m-%d")
            state_str = "🟢 LOW TARIFF" if switch["state"] else "🔴 NORMAL"
            status_str = "✅ Past" if switch["is_past"] else "⏰ Future"
            
            print(f"│ {date_str} {time_str:>8} │ {state_str:^13} │ {status_str:^8} │")
        
        print("└──────────────────────┴───────────────┴──────────┘")
        
        # Current status
        current_state = False
        next_switch = None
        
        for switch in today_switches:
            if switch["is_past"]:
                current_state = switch["state"]
            elif next_switch is None:
                next_switch = switch["time"]
                break
        
        print(f"\n🚦 Current Status:")
        print(f"   📊 Low tariff active: {'🟢 YES' if current_state else '🔴 NO'}")
        
        if next_switch:
            time_until = next_switch - now
            hours = int(time_until.total_seconds() // 3600)
            minutes = int((time_until.total_seconds() % 3600) // 60)
            print(f"   ⏰ Next switch: {next_switch.strftime('%H:%M')} (in {hours}h {minutes}m)")
        else:
            print(f"   ⏰ Next switch: No more switches today")
        
    else:
        print(f"\n📅 No HDO switches scheduled for today")
    
    # Tomorrow's switches
    tomorrow = today + timedelta(days=1)
    tomorrow_switches = [s for s in switches if s["date"] == tomorrow]
    
    if tomorrow_switches:
        print(f"\n📅 Tomorrow's HDO Schedule ({len(tomorrow_switches)} switches):")
        print("┌──────────────────────┬───────────────┐")
        print("│        Time          │     State     │")
        print("├──────────────────────┼───────────────┤")
        
        for switch in tomorrow_switches:
            time_str = switch["time"].strftime("%H:%M")
            date_str = switch["time"].strftime("%Y-%m-%d")
            state_str = "🟢 LOW TARIFF" if switch["state"] else "🔴 NORMAL"
            
            print(f"│ {date_str} {time_str:>8} │ {state_str:^13} │")
        
        print("└──────────────────────┴───────────────┘")


async def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python test_api_simple.py <EAN_CODE>")
        print("Example: python test_api_simple.py 859182400123456789")
        sys.exit(1)
    
    ean = sys.argv[1]
    
    print("="*60)
    print(f"🏠 CEZ HDO API Simple Test - EAN: {ean}")
    print("="*60)
    
    print("📡 Fetching data from CEZ API...")
    
    data = await get_cez_data(ean)
    
    if data:
        print("✅ Data received successfully!")
        print_simple_table(data)
    else:
        print("❌ Failed to get data from API")
        return 1
    
    print("\n" + "="*60)
    print("🎉 Test completed!")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
