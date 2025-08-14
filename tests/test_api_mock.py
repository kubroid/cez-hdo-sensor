#!/usr/bin/env python3
"""Mock data test for CEZ HDO API parser with sample data."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Mock data для тестирования (пример реального ответа API)
MOCK_API_RESPONSE = {
    "signals": [
        {"time": "2025-08-14T06:00:00", "state": True},   # 06:00 - LOW TARIFF ON
        {"time": "2025-08-14T08:00:00", "state": False},  # 08:00 - LOW TARIFF OFF
        {"time": "2025-08-14T13:00:00", "state": True},   # 13:00 - LOW TARIFF ON
        {"time": "2025-08-14T16:00:00", "state": False},  # 16:00 - LOW TARIFF OFF
        {"time": "2025-08-14T20:00:00", "state": True},   # 20:00 - LOW TARIFF ON
        {"time": "2025-08-14T22:00:00", "state": False},  # 22:00 - LOW TARIFF OFF
        {"time": "2025-08-15T02:00:00", "state": True},   # 02:00 - LOW TARIFF ON (tomorrow)
        {"time": "2025-08-15T05:00:00", "state": False},  # 05:00 - LOW TARIFF OFF (tomorrow)
        {"time": "2025-08-15T06:00:00", "state": True},   # 06:00 - LOW TARIFF ON (tomorrow)
        {"time": "2025-08-15T08:00:00", "state": False},  # 08:00 - LOW TARIFF OFF (tomorrow)
    ]
}


class CezHdoApiMock:
    """Mock CEZ HDO API client for testing."""

    def __init__(self, ean: str) -> None:
        """Initialize the mock API client."""
        self.ean = ean

    def parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
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
            if total_seconds > 0:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                relative = f"in {hours}h {minutes}m"
            else:
                relative = "now"
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


def test_parser_with_mock_data():
    """Test the parser with mock data."""
    print_table_header("🧪 CEZ HDO API Parser Test - Mock Data")
    
    api = CezHdoApiMock("859182400123456789")
    
    try:
        print("📊 Processing mock API response...")
        
        # Parse mock data
        parsed_data = api.parse_response(MOCK_API_RESPONSE)
        
        if not parsed_data:
            print("❌ Failed to parse mock data")
            return False
        
        print("✅ Mock data parsed successfully!")
        
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
        
        # Mock data info
        signals_count = len(MOCK_API_RESPONSE.get("signals", []))
        print(f"\n🔍 Mock Data Info:")
        print(f"   📊 Total signals in mock response: {signals_count}")
        print(f"   📅 Mock data covers: 2 days")
        print(f"   🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Raw mock data
        print(f"\n📋 Raw Mock Data:")
        print(json.dumps(MOCK_API_RESPONSE, indent=2, ensure_ascii=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False


def main():
    """Main function."""
    success = test_parser_with_mock_data()
    
    print("\n" + "="*80)
    if success:
        print("🎉 Mock data test completed successfully!")
        print("💡 This demonstrates how the parser would work with real API data")
    else:
        print("💥 Mock data test failed!")
    print("="*80)


if __name__ == "__main__":
    main()
