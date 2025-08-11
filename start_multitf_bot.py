#!/usr/bin/env python3
"""
Startup script for Multi-Timeframe OTC Signal Bot
Run this to start the advanced bot with automatic restart on errors
"""

import subprocess
import sys
import time
import os

def start_bot():
    """Start the multi-timeframe OTC signal bot"""
    print("🤖 Starting Multi-Timeframe OTC Signal Bot...")
    print("=" * 60)
    
    if not os.path.exists("otc_multitf_bot.py"):
        print("❌ Error: otc_multitf_bot.py not found!")
        print("Make sure you're in the correct directory")
        return False
    
    # Check for required packages
    try:
        import pandas
        import pandas_ta
        import numpy
        import aiohttp
        import asyncio
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install python-telegram-bot==13.15 pandas pandas_ta numpy aiohttp")
        return False
    
    try:
        print("🚀 Launching multi-timeframe bot...")
        print("Features: FVG detection, multi-TF analysis, advanced scoring")
        result = subprocess.run([sys.executable, "otc_multitf_bot.py"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Bot exited normally")
        else:
            print(f"⚠️ Bot exited with code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False
    
    return True

def main():
    """Main function with restart logic"""
    restart_count = 0
    max_restarts = 5
    
    print("🌟 Multi-Timeframe OTC Signal Bot")
    print("Advanced features: FVG + Breakout + Multi-TF Analysis")
    print()
    
    while restart_count < max_restarts:
        if start_bot():
            break
            
        restart_count += 1
        if restart_count < max_restarts:
            print(f"\n🔄 Restarting bot in 10 seconds... (attempt {restart_count}/{max_restarts})")
            time.sleep(10)
        else:
            print(f"\n❌ Maximum restart attempts ({max_restarts}) reached")
            print("Please check your configuration and try again manually")
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
