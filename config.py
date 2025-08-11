# ========== MULTI-TIMEFRAME OTC SIGNAL BOT CONFIGURATION ==========

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
    "5s": 5,        # 5 seconds - for sniper entries
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
SNIPER_TF = "5s"    # Sniper Timeframe (precise entries)

# Signal Settings
CANDLES_N = 200                    # History length per timeframe
POLL_INTERVAL = 45.0               # 45 seconds between polls (much slower for quality)
SIGNAL_DEBOUNCE = 1800             # 30 minutes between same pair signals (much slower, higher quality)

# Technical Indicator Parameters
MIN_SIGNAL_SCORE = 97              # Extremely high threshold for premium signals only
TREND_STRENGTH_THRESHOLD = 0.97    # Extremely strong trend requirement
VOLATILITY_THRESHOLD = 0.007       # Higher volatility threshold for premium moves
CONFIRMATION_CANDLES = 9           # More confirmation candles required
MIN_VOLUME_RATIO = 3.5             # Higher volume confirmation
TREND_ALIGNMENT_REQUIRED = True    # All timeframes must align
ENTRY_TIMEFRAME = "30s"            # Focus on 30-second entry trades

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
