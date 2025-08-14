#!/usr/bin/env python3
"""Test script for CEZ HDO API with real data structure."""

import json
from datetime import datetime, timedelta, time

# Реальные данные из API
REAL_API_RESPONSE = {
    "data": {
        "signals": [
            {
                "signal": "a3b4dp01",
                "den": "Čtvrtek",
                "datum": "14.08.2025",
                "casy": "00:00-05:35;   06:30-08:55;   09:54-15:16;   16:15-20:16;   21:15-24:00"
            },
            {
                "signal": "a3b4dp01",
                "den": "Pátek",
                "datum": "15.08.2025",
                "casy": "00:00-05:35;   06:30-08:55;   09:54-15:16;   16:15-20:16;   21:15-24:00"
            },
            {
                "signal": "a3b4dp02",
                "den": "Čtvrtek",
                "datum": "14.08.2025",
                "casy": "00:00-05:35;   06:30-08:55;   09:54-15:16;   16:15-20:16;   21:15-24:00"
            },
            {
                "signal": "a3b4dp06",
                "den": "Čtvrtek",
                "datum": "14.08.2025",
                "casy": "01:10-05:11;   11:35-13:56;   22:10-23:51;"
            }
        ],
        "amm": False,
        "switchClock": False,
        "unknown": False,
        "partner": "0022403920",
        "vkont": "000058075110",
        "vstelle": "1000017470",
        "anlage": "0100046045"
    },
    "statusCode": 200,
    "flashMessages": []
}


class CezHdoApiFixed:
    """Fixed CEZ HDO API client."""

    def __init__(self, ean: str, signal: str = "a3b4dp01") -> None:
        """Initialize the API client."""
        self.ean = ean
        self.signal = signal

    def parse_response(self, data: dict) -> dict:
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


def print_schedule_table(switches, title="HDO Schedule"):
    """Print a formatted table of switches."""
    if not switches:
        print(f"\n📅 {title}: No switches")
        return
    
    print(f"\n📅 {title} ({len(switches)} switches):")
    print("┌─────────┬───────────────┬──────────────┐")
    print("│  Time   │     State     │   Duration   │")
    print("├─────────┼───────────────┼──────────────┤")
    
    for i, switch in enumerate(switches):
        time_str = switch["time"].strftime("%H:%M")
        state = "🟢 LOW TARIFF" if switch["state"] else "🔴 NORMAL"
        
        # Calculate duration to next switch
        duration = ""
        if i < len(switches) - 1:
            next_switch = switches[i + 1]
            delta = (next_switch["time"] - switch["time"]).total_seconds() / 3600
            duration = f"{delta:.1f}h"
        else:
            duration = "Until next day"
        
        print(f"│ {time_str:^7} │ {state:^13} │ {duration:^12} │")
    
    print("└─────────┴───────────────┴──────────────┘")


def test_real_data():
    """Test with real API response structure."""
    print("="*60)
    print("🏠 CEZ HDO API Test - Real Data Structure")
    print("="*60)
    
    # Test different signals
    signals_to_test = ["a3b4dp01", "a3b4dp02", "a3b4dp06"]
    
    for signal in signals_to_test:
        print(f"\n🔍 Testing signal: {signal}")
        print("-" * 40)
        
        api = CezHdoApiFixed("859182400123456789", signal)
        parsed_data = api.parse_response(REAL_API_RESPONSE)
        
        if parsed_data["today_switches"]:
            print(f"\n📊 Summary for {signal}:")
            print(f"   Low tariff active: {'🟢 YES' if parsed_data['is_low_tariff'] else '🔴 NO'}")
            print(f"   Current period: {parsed_data['current_period'].replace('_', ' ').title()}")
            
            next_switch = parsed_data.get('next_switch')
            if next_switch:
                time_until = next_switch - datetime.now()
                if time_until.total_seconds() > 0:
                    hours = int(time_until.total_seconds() // 3600)
                    minutes = int((time_until.total_seconds() % 3600) // 60)
                    print(f"   Next switch: {next_switch.strftime('%H:%M')} (in {hours}h {minutes}m)")
                else:
                    print(f"   Next switch: {next_switch.strftime('%H:%M')} (past)")
            else:
                print(f"   Next switch: No more switches today")
            
            print_schedule_table(parsed_data["today_switches"], f"Today's {signal} Schedule")
        
        print("\n" + "="*60)


def main():
    """Main function."""
    print(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_real_data()
    print("🎉 Test completed!")


if __name__ == "__main__":
    main()
