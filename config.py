# ========== MULTI-TIMEFRAME OTC SIGNAL BOT CONFIGURATION ==========
# Copy this file to config.py and fill in your actual values

# Telegram Bot Configuration
TELEGRAM_TOKEN = "8252758490:AAE2u3DwM_xYqCXnkllKmxyw7k6_LI0zcoo"
TELEGRAM_CHAT_ID = "6789225017"  # Your user ID or group ID

# Pocket Option API Configuration
POCKET_OPTION_EMAIL = "gripcake@gmail.com"  # Replace with your Pocket Option email
POCKET_OPTION_PASSWORD = "Franklin5"        # Replace with your Pocket Option password
POCKET_OPTION_DEMO = True                       # Set to False for real account

# Trading Pairs to Monitor
PAIRS = [
    "EURUSD-OTC",    # Replace with actual Pocket Option pair names
    "USDJPY-OTC",    # Replace with actual Pocket Option pair names
    "GBPUSD-OTC",    # Add more pairs as needed
]

# Timeframe Definitions (in seconds)
TF_DEFS = {
    "30s": 30,      # 30 seconds
    "1m": 60,       # 1 minute
    "3m": 180,      # 3 minutes
    "5m": 300,      # 5 minutes
}

# Which Timeframes to Use for Decision Making
HTF = "5m"          # High Timeframe (trend direction)
MTF = "1m"          # Medium Timeframe (main analysis)
LTF = "30s"         # Low Timeframe (entry refinement)

# Signal Settings
CANDLES_N = 200                    # History length per timeframe
POLL_INTERVAL = 1.0                # Seconds between polls for new candles
SIGNAL_DEBOUNCE = 60 * 3           # 3 minutes between same pair signals

# Breakout Detection Parameters
HTF_RANGE_BARS = 20                # Bars to look back for range calculation
BREAKOUT_BODY_RATIO = 0.35         # Minimum body % of candle range required

# Keltner Channel Parameters
EMA_LEN = 20                       # EMA length for center line
ATR_LEN = 10                       # ATR length for volatility
KC_MULT = 1.5                      # ATR multiplier for upper/lower bands

# ========== HOW TO SETUP ==========
# 1. Create a Telegram bot with @BotFather
# 2. Get your bot token
# 3. Get your chat ID (send a message to @userinfobot)
# 4. Replace the placeholder values above
# 5. Save as config.py
# 6. Run: python otc_multitf_bot.py

# ========== EXAMPLE VALUES ==========
# TELEGRAM_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
# TELEGRAM_CHAT_ID = "123456789"
# PAIRS = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC"]

# ========== ADVANCED FEATURES ==========
# This bot includes:
# - Multi-timeframe analysis (30s, 1m, 3m, 5m)
# - Fair Value Gap (FVG) detection
# - Swing Support/Resistance zone clustering
# - Breakout detection with body ratio validation
# - Advanced scoring system combining multiple factors
# - Asynchronous architecture for better performance
# - Automatic FVG expiration and filling detection
