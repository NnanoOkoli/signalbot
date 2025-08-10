import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Pocket Option API Configuration
    POCKET_OPTION_EMAIL = os.getenv('POCKET_OPTION_EMAIL', '')
    POCKET_OPTION_PASSWORD = os.getenv('POCKET_OPTION_PASSWORD', '')
    
    # Trading Parameters
    DEFAULT_INVESTMENT = float(os.getenv('DEFAULT_INVESTMENT', '10'))  # USD
    MAX_INVESTMENT = float(os.getenv('MAX_INVESTMENT', '100'))  # USD
    MIN_INVESTMENT = float(os.getenv('MIN_INVESTMENT', '1'))  # USD
    
    # Risk Management
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '50'))  # USD
    MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '20'))
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', '5'))  # 5%
    
    # Signal Parameters
    EXPIRY_TIME = int(os.getenv('EXPIRY_TIME', '5'))  # minutes
    SIGNAL_CONFIDENCE_THRESHOLD = float(os.getenv('SIGNAL_CONFIDENCE_THRESHOLD', '0.7'))  # 70%
    
    # Technical Indicators
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    
    MACD_FAST = int(os.getenv('MACD_FAST', '12'))
    MACD_SLOW = int(os.getenv('MACD_SLOW', '26'))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', '9'))
    
    BOLLINGER_PERIOD = int(os.getenv('BOLLINGER_PERIOD', '20'))
    BOLLINGER_STD = float(os.getenv('BOLLINGER_STD', '2.0'))
    
    # OTC Specific Settings
    OTC_ANALYSIS_PERIOD = int(os.getenv('OTC_ANALYSIS_PERIOD', '100'))  # candles
    TREND_STRENGTH_THRESHOLD = float(os.getenv('TREND_STRENGTH_THRESHOLD', '0.6'))
    
    # Time Settings
    MARKET_OPEN_HOUR = int(os.getenv('MARKET_OPEN_HOUR', '0'))  # UTC
    MARKET_CLOSE_HOUR = int(os.getenv('MARKET_CLOSE_HOUR', '23'))  # UTC
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'signal_bot.log')
    
    # Assets to trade
    TRADING_ASSETS = [
        'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF',
        'AUD/USD', 'USD/CAD', 'NZD/USD', 'EUR/GBP',
        'EUR/JPY', 'GBP/JPY', 'CHF/JPY', 'AUD/JPY'
    ]
    
    # Signal Types
    SIGNAL_TYPES = {
        'STRONG_BUY': 0.9,
        'BUY': 0.7,
        'WEAK_BUY': 0.6,
        'NEUTRAL': 0.5,
        'WEAK_SELL': 0.4,
        'SELL': 0.3,
        'STRONG_SELL': 0.1
    }
