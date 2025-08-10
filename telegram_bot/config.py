"""
Enhanced Telegram Bot Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Validate bot token
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN not found! Please create a .env file with your bot token:\n"
        "BOT_TOKEN=your_telegram_bot_token_here"
    )

# Pocket Option API Configuration
POCKET_OPTION_EMAIL = os.getenv('POCKET_OPTION_EMAIL')
POCKET_OPTION_PASSWORD = os.getenv('POCKET_OPTION_PASSWORD')
POCKET_OPTION_DEMO = os.getenv('POCKET_OPTION_DEMO', 'true').lower() == 'true'

# Validate Pocket Option credentials
if not POCKET_OPTION_EMAIL or not POCKET_OPTION_PASSWORD:
    print("⚠️  Warning: Pocket Option credentials not found in .env file")
    print("   The trading bot will not be able to connect to Pocket Option")
    print("   Add POCKET_OPTION_EMAIL and POCKET_OPTION_PASSWORD to your .env file")

# Bot Settings
BOT_NAME = "Pocket Option Trading Bot"
BOT_VERSION = "2.0.0"
BOT_DESCRIPTION = "A feature-rich Telegram bot with Pocket Option trading integration"

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Message Settings
MAX_MESSAGE_LENGTH = 4096
DEFAULT_TIMEOUT = 30

# Available Commands
COMMANDS = {
    'start': 'Start the bot and see trading options',
    'help': 'Show comprehensive help with all commands',
    'connect': 'Connect to Pocket Option',
    'disconnect': 'Disconnect from Pocket Option',
    'balance': 'Check account balance',
    'buy': 'Place a CALL trade (e.g., /buy EURUSD 1m 10)',
    'sell': 'Place a PUT trade (e.g., /sell GBPUSD 5m 25)',
    'trades': 'View active trades',
    'history': 'View trading history',
    'status': 'Check bot and connection status'
}

# Command Categories
COMMAND_CATEGORIES = {
    'Basic': ['start', 'help', 'status'],
    'Trading': ['buy', 'sell', 'balance', 'trades', 'history'],
    'Connection': ['connect', 'disconnect']
}

# Bot Features
FEATURES = [
    'Pocket Option WebSocket integration',
    'Real-time trading commands',
    'Balance monitoring',
    'Trade management',
    'Inline keyboards for quick actions',
    'Professional logging',
    'Error handling',
    'Markdown formatting'
]

# Trading Settings
TRADING_SETTINGS = {
    'min_amount': 1.0,
    'max_amount': 10000.0,
    'default_expiry': 60,  # 1 minute
    'supported_timeframes': ['1m', '5m', '15m', '1h', '4h', '1d'],
    'max_active_trades': 10
}

# Calculator Settings
CALC_MAX_EXPRESSION_LENGTH = 100
CALC_ALLOWED_FUNCTIONS = ['sqrt', 'abs', 'round', 'min', 'max']

# Random Number Settings
RANDOM_MAX_RANGE = 1000000
RANDOM_MIN_RANGE = 1
