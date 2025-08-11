# ========== MULTI-TIMEFRAME OTC SIGNAL BOT CONFIGURATION ==========
# Copy this file to config.py and fill in your actual values

# Telegram Bot Configuration
TELEGRAM_TOKEN = "8252758490:AAE2u3DwM_xYqCXnkllKmxyw7k6_LI0zcoo"
TELEGRAM_CHAT_ID = "6789225017"  # Your user ID or group ID

# Pocket Option API Configuration
POCKET_OPTION_EMAIL = "gripcake@gmail.com"  # Replace with your Pocket Option email
POCKET_OPTION_PASSWORD = "Franklin5"        # Replace with your Pocket Option password
POCKET_OPTION_DEMO = True                       # Set to False for real account

# Trading Pairs to Monitor - ALL OTC PAIRS
PAIRS = [
    "EURUSD-OTC",    # Euro/US Dollar
    "GBPUSD-OTC",    # British Pound/US Dollar
    "USDJPY-OTC",    # US Dollar/Japanese Yen
    "USDCHF-OTC",    # US Dollar/Swiss Franc
    "AUDUSD-OTC",    # Australian Dollar/US Dollar
    "USDCAD-OTC",    # US Dollar/Canadian Dollar
    "NZDUSD-OTC",    # New Zealand Dollar/US Dollar
    "EURGBP-OTC",    # Euro/British Pound
    "EURJPY-OTC",    # Euro/Japanese Yen
    "GBPJPY-OTC",    # British Pound/Japanese Yen
    "AUDJPY-OTC",    # Australian Dollar/Japanese Yen
    "CADJPY-OTC",    # Canadian Dollar/Japanese Yen
    "EURCAD-OTC",    # Euro/Canadian Dollar
    "GBPCAD-OTC",    # British Pound/Canadian Dollar
    "AUDCAD-OTC",    # Australian Dollar/Canadian Dollar
    "EURAUD-OTC",    # Euro/Australian Dollar
    "GBPAUD-OTC",    # British Pound/Australian Dollar
    "EURNZD-OTC",    # Euro/New Zealand Dollar
    "GBPNZD-OTC",    # British Pound/New Zealand Dollar
    "AUDNZD-OTC",    # Australian Dollar/New Zealand Dollar
]

# Timeframe Definitions (in seconds)
TF_DEFS = {
    "30s": 30,      # 30 seconds
    "1m": 60,       # 1 minute
    "3m": 180,      # 3 minutes
    "5m": 300,      # 5 minutes
    "15m": 900,     # 15 minutes
}

# Which Timeframes to Use for Decision Making
HTF = "15m"         # High Timeframe (trend direction)
MTF = "5m"          # Medium Timeframe (main analysis)
LTF = "1m"          # Low Timeframe (entry refinement)

# Signal Settings
CANDLES_N = 200                    # History length per timeframe
POLL_INTERVAL = 0.5                # Seconds between polls for new candles (faster)
SIGNAL_DEBOUNCE = 60 * 2           # 2 minutes between same pair signals (more frequent)

# Technical Indicator Parameters
RSI_PERIOD = 14                    # RSI calculation period
RSI_OVERBOUGHT = 70               # RSI overbought threshold
RSI_OVERSOLD = 30                 # RSI oversold threshold

MACD_FAST = 12                    # MACD fast EMA
MACD_SLOW = 26                    # MACD slow EMA
MACD_SIGNAL = 9                   # MACD signal line

BOLLINGER_PERIOD = 20             # Bollinger Bands period
BOLLINGER_STD = 2                 # Bollinger Bands standard deviation

STOCHASTIC_K = 14                 # Stochastic %K period
STOCHASTIC_D = 3                  # Stochastic %D period



CCI_PERIOD = 20                   # Commodity Channel Index period

# Breakout Detection Parameters
HTF_RANGE_BARS = 20                # Bars to look back for range calculation
BREAKOUT_BODY_RATIO = 0.35         # Minimum body % of candle range required

# Keltner Channel Parameters
EMA_LEN = 20                       # EMA length for center line
ATR_LEN = 10                       # ATR length for volatility
KC_MULT = 1.5                      # ATR multiplier for upper/lower bands

# Signal Generation Thresholds
MIN_SIGNAL_SCORE = 70              # Minimum score to generate signal
TREND_STRENGTH_THRESHOLD = 0.6     # Minimum trend strength required
VOLATILITY_THRESHOLD = 0.002       # Minimum price movement required

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
