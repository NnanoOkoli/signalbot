#!/usr/bin/env python3
"""
Startup script for Integrated Multi-Timeframe OTC Signal Bot with Pocket Option API
Run this to start the advanced bot with real market data integration
"""
import subprocess
import sys
import time
import os

def start_bot():
    """Start the integrated Pocket Option OTC signal bot"""
    print("🤖 Starting Integrated OTC Signal Bot with Pocket Option API...")
    print("=" * 70)
    
    # Check if required files exist
    if not os.path.exists("otc_multitf_pocket_bot.py"):
        print("❌ Error: otc_multitf_pocket_bot.py not found!")
        print("Make sure you're in the correct directory")
        return False
    
    if not os.path.exists("pocket_option_api.py"):
        print("❌ Error: pocket_option_api.py not found!")
        print("This file is required for Pocket Option integration")
        return False
    
    if not os.path.exists("config.py"):
        print("❌ Error: config.py not found!")
        print("Please copy config_multitf_template.py to config.py and configure it")
        return False
    
    # Check required packages
    try:
        import pandas
        import pandas_ta
        import numpy
        import aiohttp
        import asyncio
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install pandas pandas_ta numpy aiohttp")
        return False
    
    # Check configuration
    try:
        from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, POCKET_OPTION_EMAIL, POCKET_OPTION_PASSWORD
        print("✅ Configuration loaded")
        
        # Check if credentials are configured
        if TELEGRAM_CHAT_ID == "YOUR_ACTUAL_CHAT_ID_HERE":
            print("⚠️  Warning: Chat ID not configured")
            print("   Get your chat ID from @userinfobot on Telegram")
        
        if POCKET_OPTION_EMAIL == "your_email@example.com":
            print("⚠️  Warning: Pocket Option credentials not configured")
            print("   Update config.py with your Pocket Option email and password")
        
    except ImportError as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    try:
        print("🚀 Launching integrated Pocket Option bot...")
        result = subprocess.run([sys.executable, "otc_multitf_pocket_bot.py"], 
                               capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Bot exited normally")
        else:
            print(f"⚠️  Bot exited with code: {result.returncode}")
            
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
