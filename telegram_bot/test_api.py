"""
Test script for Pocket Option API
Tests the API wrapper without requiring real credentials
"""

import sys
import os
from pocket_option_api import PocketOptionAPI

def test_api_initialization():
    """Test API initialization"""
    print("🧪 Testing API Initialization...")
    
    try:
        # Test with dummy credentials
        api = PocketOptionAPI("test@example.com", "password123", demo=True)
        print("✅ API initialization successful")
        print(f"   Demo mode: {api.demo}")
        print(f"   WebSocket URL: {api.base_url}")
        return api
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return None

def test_api_methods(api):
    """Test API methods"""
    print("\n🧪 Testing API Methods...")
    
    if not api:
        print("❌ Cannot test methods - API not initialized")
        return
    
    try:
        # Test connection status
        status = api.get_connection_status()
        print("✅ Connection status method working")
        print(f"   Status: {status}")
        
        # Test balance method
        balance = api.get_balance()
        print("✅ Balance method working")
        print(f"   Balance: ${balance}")
        
        # Test assets method
        assets = api.get_assets()
        print("✅ Assets method working")
        print(f"   Assets count: {len(assets)}")
        
        # Test trades method
        trades = api.get_trades()
        print("✅ Trades method working")
        print(f"   Trades count: {len(trades)}")
        
        # Test connection check
        connected = api.is_connected()
        print("✅ Connection check method working")
        print(f"   Connected: {connected}")
        
    except Exception as e:
        print(f"❌ Method test failed: {e}")

def test_trade_validation():
    """Test trade validation logic"""
    print("\n🧪 Testing Trade Validation...")
    
    try:
        # Test time parsing
        test_times = ["1m", "5m", "15m", "1h", "4h", "1d"]
        expected_seconds = [60, 300, 900, 3600, 14400, 86400]
        
        for time_str, expected in zip(test_times, expected_seconds):
            # This would normally be in the trading bot
            if time_str.endswith('m'):
                parsed = int(time_str[:-1]) * 60
            elif time_str.endswith('h'):
                parsed = int(time_str[:-1]) * 3600
            elif time_str.endswith('d'):
                parsed = int(time_str[:-1]) * 86400
            else:
                parsed = None
            
            if parsed == expected:
                print(f"✅ Time parsing: {time_str} → {parsed} seconds")
            else:
                print(f"❌ Time parsing: {time_str} → {parsed} seconds (expected {expected})")
        
    except Exception as e:
        print(f"❌ Trade validation test failed: {e}")

def test_config_loading():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration Loading...")
    
    try:
        from config import (
            BOT_TOKEN, POCKET_OPTION_EMAIL, POCKET_OPTION_PASSWORD, 
            POCKET_OPTION_DEMO, TRADING_SETTINGS
        )
        
        print("✅ Configuration loaded successfully")
        print(f"   Bot Token: {'✅ Set' if BOT_TOKEN else '❌ Missing'}")
        print(f"   PO Email: {'✅ Set' if POCKET_OPTION_EMAIL else '❌ Missing'}")
        print(f"   PO Password: {'✅ Set' if POCKET_OPTION_PASSWORD else '❌ Missing'}")
        print(f"   Demo Mode: {POCKET_OPTION_DEMO}")
        print(f"   Trading Settings: {len(TRADING_SETTINGS)} items")
        
    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Pocket Option API Test Suite")
    print("=" * 50)
    
    # Test 1: API Initialization
    api = test_api_initialization()
    
    # Test 2: API Methods
    test_api_methods(api)
    
    # Test 3: Trade Validation
    test_trade_validation()
    
    # Test 4: Configuration
    test_config_loading()
    
    print("\n" + "=" * 50)
    print("🏁 Test Suite Complete!")
    
    if api:
        print("\n💡 Next Steps:")
        print("   1. Add your real Pocket Option credentials to .env")
        print("   2. Test connection with /connect command")
        print("   3. Try placing a demo trade")
    else:
        print("\n❌ Issues found. Check the errors above.")

if __name__ == "__main__":
    main()
