#!/usr/bin/env python3
"""
Startup script for OTC Signal Bot
Run this to start the bot with automatic restart on errors
"""

import subprocess
import sys
import time
import os

def start_bot():
    """Start the OTC signal bot"""
    print("🤖 Starting OTC Signal Bot...")
    print("=" * 50)
    
    # Check if main bot file exists
    if not os.path.exists("otc_signal_bot.py"):
        print("❌ Error: otc_signal_bot.py not found!")
        print("Make sure you're in the correct directory")
        return False
    
    # Check if required packages are installed
    try:
        import pandas
        import pandas_ta
        from telegram import Bot
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install python-telegram-bot==13.15 pandas pandas_ta websocket-client")
        return False
    
    # Start the bot
    try:
        print("🚀 Launching bot...")
        result = subprocess.run([sys.executable, "otc_signal_bot.py"], 
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
