# ========== OTC SIGNAL BOT CONFIGURATION ==========
# Copy this file to config.py and fill in your actual values

# Telegram Bot Configuration
TELEGRAM_TOKEN = "YOUR_ACTUAL_BOT_TOKEN_HERE"  # Get from @BotFather
TELEGRAM_CHAT_ID = "YOUR_ACTUAL_CHAT_ID_HERE"  # Your user ID or group ID

# Trading Pairs to Monitor
PAIRS = [
    "EURUSD-OTC",    # Replace with actual Pocket Option pair names
    "USDJPY-OTC",    # Replace with actual Pocket Option pair names
    "GBPUSD-OTC",    # Add more pairs as needed
]

# Signal Settings
POLL_INTERVAL = 30                    # Seconds between checks (30 = 2 checks per minute)
SIGNAL_DEBOUNCE_SECONDS = 60 * 3     # 3 minutes between same signal types
MAX_CONSECUTIVE_ERRORS = 5            # Max errors before cooldown
ERROR_COOLDOWN = 60                   # Seconds to wait after multiple errors

# ========== HOW TO SETUP ==========
# 1. Create a Telegram bot with @BotFather
# 2. Get your bot token
# 3. Get your chat ID (send a message to @userinfobot)
# 4. Replace the placeholder values above
# 5. Save as config.py
# 6. Run: python start_bot.py

# ========== EXAMPLE VALUES ==========
# TELEGRAM_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
# TELEGRAM_CHAT_ID = "123456789"
# PAIRS = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC"]
