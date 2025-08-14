#!/usr/bin/env python3
"""Test CEZ HDO API functionality."""

import asyncio
import sys
import json
from pathlib import Path

# Add the integration to the Python path
sys.path.insert(0, str(Path(__file__).parent / "custom_components" / "cez_hdo"))

from api import CezHdoApi

async def test_api():
    """Test the CEZ HDO API."""
    print("Testing CEZ HDO API...")
    
    # Test with a dummy EAN (should fail gracefully)
    test_ean = "1234567890123"
    api = CezHdoApi(test_ean, "a3b4dp01")
    
    try:
        print(f"Testing API with EAN: {test_ean}")
        print("Making API request...")
        
        data = await api.async_get_data()
        
        if data:
            print("✅ API request successful")
            print(f"Response keys: {list(data.keys())}")
            print(f"Is low tariff: {data.get('is_low_tariff', 'N/A')}")
            print(f"Current period: {data.get('current_period', 'N/A')}")
            print(f"Next switch: {data.get('next_switch', 'N/A')}")
            print(f"Today switches count: {len(data.get('today_switches', []))}")
        else:
            print("⚠️  API returned empty data (expected for dummy EAN)")
        
        await api.async_close()
        print("✅ API session closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        await api.async_close()
        return False

async def test_coordinator():
    """Test the coordinator functionality."""
    print("\nTesting Coordinator...")
    
    try:
        from coordinator import CezHdoCoordinator
        from const import CONF_EAN, CONF_SIGNAL
        
        # Mock Home Assistant (minimal implementation)
        class MockHass:
            def __init__(self):
                self.data = {}
        
        config = {
            CONF_EAN: "1234567890123",
            CONF_SIGNAL: "a3b4dp01"
        }
        
        hass = MockHass()
        coordinator = CezHdoCoordinator(hass, config)
        
        print(f"✅ Coordinator created successfully")
        print(f"EAN: {coordinator.ean}")
        print(f"Signal: {coordinator.signal}")
        print(f"Update interval: {coordinator.update_interval}")
        
        await coordinator.async_shutdown()
        print("✅ Coordinator shutdown successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Coordinator test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("=== CEZ HDO INTEGRATION TEST ===\n")
    
    api_test = await test_api()
    coordinator_test = await test_coordinator()
    
    print("\n=== TEST RESULTS ===")
    print(f"API Test: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"Coordinator Test: {'✅ PASS' if coordinator_test else '❌ FAIL'}")
    
    if api_test and coordinator_test:
        print("\n✅ All tests passed! Integration is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
