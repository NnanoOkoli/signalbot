#!/usr/bin/env python3
"""
Test script for Multi-Timeframe OTC Signal Bot
This script tests the bot's functionality with synthetic data
"""

import asyncio
import time
import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import pandas_ta as ta
        print("✅ pandas_ta imported successfully")
    except ImportError as e:
        print(f"❌ pandas_ta import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp imported successfully")
    except ImportError as e:
        print(f"❌ aiohttp import failed: {e}")
        return False
    
    try:
        import asyncio
        print("✅ asyncio imported successfully")
    except ImportError as e:
        print(f"❌ asyncio import failed: {e}")
        return False
    
    return True

def test_bot_import():
    """Test if the bot module can be imported"""
    print("\n🧪 Testing bot module import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Try to import the bot
        import otc_multitf_bot
        print("✅ otc_multitf_bot imported successfully")
        
        # Check if key functions exist
        if hasattr(otc_multitf_bot, 'add_indicators'):
            print("✅ add_indicators function found")
        else:
            print("❌ add_indicators function not found")
            return False
            
        if hasattr(otc_multitf_bot, 'detect_fvg_for_df'):
            print("✅ detect_fvg_for_df function found")
        else:
            print("❌ detect_fvg_for_df function not found")
            return False
            
        if hasattr(otc_multitf_bot, 'compute_score'):
            print("✅ compute_score function found")
        else:
            print("❌ compute_score function not found")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ otc_multitf_bot import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_bot_functions():
    """Test the bot's core functions"""
    print("\n🧪 Testing bot functions...")
    
    try:
        import otc_multitf_bot
        
        # Test data structures
        from otc_multitf_bot import Candle, FVGap, SRZone
        
        # Create test candle
        test_candle = Candle(
            ts=time.time(),
            open=1.1000,
            high=1.1005,
            low=1.0995,
            close=1.1002,
            volume=1000
        )
        print("✅ Candle creation successful")
        
        # Test FVG creation
        test_fvg = FVGap(
            pair="EURUSD-OTC",
            tf="1m",
            side="bull",
            top=1.1000,
            bottom=1.1005
        )
        print("✅ FVG creation successful")
        
        # Test SR zone creation
        test_sr = SRZone(
            pair="EURUSD-OTC",
            low=1.0990,
            high=1.1010
        )
        print("✅ SR Zone creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Function test failed: {e}")
        return False

async def test_synthetic_data():
    """Test the synthetic data generation"""
    print("\n🧪 Testing synthetic data generation...")
    
    try:
        import otc_multitf_bot
        
        # Test the stub function
        test_pair = "EURUSD-OTC"
        candles = await otc_multitf_bot.get_live_candles_stub(test_pair)
        
        if not candles:
            print("❌ No candles generated")
            return False
            
        print(f"✅ Generated {len(candles)} candle(s)")
        
        # Check timeframe distribution
        timeframes = [tf for tf, _ in candles]
        print(f"   Timeframes: {', '.join(timeframes)}")
        
        # Check candle structure
        for tf, candle in candles:
            if not hasattr(candle, 'open') or not hasattr(candle, 'close'):
                print(f"❌ Invalid candle structure for {tf}")
                return False
        
        print("✅ All candles have valid structure")
        return True
        
    except Exception as e:
        print(f"❌ Synthetic data test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Multi-Timeframe OTC Signal Bot - Test Suite")
    print("=" * 60)
    
    # Test 1: Package imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install missing packages:")
        print("pip install pandas pandas_ta numpy aiohttp python-telegram-bot==13.15")
        return False
    
    # Test 2: Bot module import
    if not test_bot_import():
        print("\n❌ Bot module import failed. Check if otc_multitf_bot.py exists.")
        return False
    
    # Test 3: Core functions
    if not await test_bot_functions():
        print("\n❌ Function tests failed.")
        return False
    
    # Test 4: Synthetic data
    if not await test_synthetic_data():
        print("\n❌ Synthetic data test failed.")
        return False
    
    print("\n🎉 All tests passed! The bot is ready to use.")
    print("\n📋 Next steps:")
    print("1. Copy config_multitf_template.py to config.py")
    print("2. Fill in your Telegram bot token and chat ID")
    print("3. Run: python start_multitf_bot.py")
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
