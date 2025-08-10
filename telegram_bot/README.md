# 🚀 Pocket Option Trading Bot

A powerful Telegram bot that integrates directly with Pocket Option for instant trading via chat commands.

## ✨ Features

- **🔗 Real-time Pocket Option Integration** - WebSocket connection for instant trade execution
- **📱 Telegram Commands** - Trade directly from your phone using simple commands
- **💰 Balance Monitoring** - Real-time account balance and trade tracking
- **📊 Trade Management** - View active trades and trading history
- **⚡ Instant Execution** - Place trades in seconds without opening the app
- **🛡️ Safety Features** - Balance checks, error handling, and validation
- **🎯 Multiple Timeframes** - Support for 1m, 5m, 15m, 1h, 4h, 1d
- **🔐 Secure Authentication** - Environment variable protection for credentials

## 🏗️ Architecture

```
Telegram Bot ←→ Pocket Option API ←→ Pocket Option WebSocket
     ↓              ↓                        ↓
User Commands   Trade Logic           Real-time Data
Inline Buttons  Validation            Market Updates
Responses       Execution             Balance Updates
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone or navigate to the bot directory
cd telegram_bot

# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp env_example.txt .env
```

### 2. Configure Credentials

Edit your `.env` file:

```env
# Telegram Bot Token
BOT_TOKEN=your_telegram_bot_token_here

# Pocket Option Credentials
POCKET_OPTION_EMAIL=your_email@example.com
POCKET_OPTION_PASSWORD=your_password
POCKET_OPTION_DEMO=true  # Set to false for real account
```

### 3. Run the Bot

```bash
# Run the trading bot
python trading_bot.py

# Or run the basic bot
python bot.py
```

## 📱 Available Commands

### 🚀 Trading Commands

| Command    | Description           | Example              |
| ---------- | --------------------- | -------------------- |
| `/buy`     | Place a CALL trade    | `/buy EURUSD 1m 10`  |
| `/sell`    | Place a PUT trade     | `/sell GBPUSD 5m 25` |
| `/balance` | Check account balance | `/balance`           |
| `/trades`  | View active trades    | `/trades`            |
| `/history` | Trading history       | `/history`           |

### ⚙️ System Commands

| Command       | Description                   | Example       |
| ------------- | ----------------------------- | ------------- |
| `/start`      | Start the bot                 | `/start`      |
| `/help`       | Show help                     | `/help`       |
| `/connect`    | Connect to Pocket Option      | `/connect`    |
| `/disconnect` | Disconnect from Pocket Option | `/disconnect` |
| `/status`     | Bot and connection status     | `/status`     |

## 💡 Trading Examples

### Basic Trades

```bash
# $10 CALL on EURUSD for 1 minute
/buy EURUSD 1m 10

# $25 PUT on GBPUSD for 5 minutes
/sell GBPUSD 5m 25

# $50 CALL on Bitcoin for 15 minutes
/buy BTCUSD 15m 50
```

### Time Formats

| Format | Duration   | Example               |
| ------ | ---------- | --------------------- |
| `1m`   | 1 minute   | `/buy EURUSD 1m 10`   |
| `5m`   | 5 minutes  | `/sell GBPUSD 5m 25`  |
| `15m`  | 15 minutes | `/buy BTCUSD 15m 50`  |
| `1h`   | 1 hour     | `/sell EURUSD 1h 100` |
| `4h`   | 4 hours    | `/buy GBPUSD 4h 200`  |
| `1d`   | 1 day      | `/sell BTCUSD 1d 500` |

## 🔧 Configuration

### Environment Variables

| Variable                 | Description            | Required | Default |
| ------------------------ | ---------------------- | -------- | ------- |
| `BOT_TOKEN`              | Telegram bot token     | ✅       | -       |
| `POCKET_OPTION_EMAIL`    | Pocket Option email    | ✅       | -       |
| `POCKET_OPTION_PASSWORD` | Pocket Option password | ✅       | -       |
| `POCKET_OPTION_DEMO`     | Use demo account       | ❌       | `true`  |

### Trading Settings

```python
TRADING_SETTINGS = {
    'min_amount': 1.0,           # Minimum trade amount
    'max_amount': 10000.0,       # Maximum trade amount
    'default_expiry': 60,        # Default expiry in seconds
    'max_active_trades': 10      # Maximum concurrent trades
}
```

## 🏛️ Project Structure

```
telegram_bot/
├── trading_bot.py          # Main trading bot (Pocket Option integration)
├── bot.py                  # Basic utility bot
├── pocket_option_api.py    # Pocket Option WebSocket API wrapper
├── config.py               # Configuration and settings
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── env_example.txt         # Environment template
└── README.md               # This file
```

## 🔌 Pocket Option API

### WebSocket Connection

- **Endpoint**: `wss://api.pocketoption.com/socket.io/?EIO=3&transport=websocket`
- **Authentication**: Email/password login
- **Protocol**: Socket.IO v3 with WebSocket transport
- **Reconnection**: Automatic reconnection on connection loss

### Trade Execution Flow

1. **User Command** → Telegram bot receives `/buy EURUSD 1m 10`
2. **Validation** → Bot validates asset, time, amount, and balance
3. **API Call** → Bot sends trade request to Pocket Option via WebSocket
4. **Confirmation** → Bot receives trade confirmation and updates user
5. **Monitoring** → Bot tracks trade status and results

## 🛡️ Safety Features

- **Balance Validation** - Prevents trades exceeding available balance
- **Input Validation** - Validates asset names, time formats, and amounts
- **Error Handling** - Comprehensive error messages and recovery
- **Connection Monitoring** - Automatic reconnection and status updates
- **Trade Limits** - Configurable minimum/maximum trade amounts

## 🚨 Important Notes

### ⚠️ Risk Warning

- **Trading involves risk** - Only trade with money you can afford to lose
- **Demo Mode Recommended** - Start with demo account to test the bot
- **Market Volatility** - Binary options are highly volatile
- **No Guarantees** - Past performance doesn't guarantee future results

### 🔐 Security

- **Never share** your `.env` file or credentials
- **Use strong passwords** for your Pocket Option account
- **Enable 2FA** on your Pocket Option account if available
- **Monitor activity** regularly for unauthorized trades

## 🐛 Troubleshooting

### Common Issues

| Issue                            | Solution                                           |
| -------------------------------- | -------------------------------------------------- |
| "Not connected to Pocket Option" | Use `/connect` command                             |
| "Authentication failed"          | Check email/password in `.env`                     |
| "Insufficient balance"           | Check your account balance                         |
| "Invalid asset"                  | Use supported asset names (EURUSD, GBPUSD, etc.)   |
| "WebSocket error"                | Check internet connection and try `/connect` again |

### Debug Mode

Enable debug logging by setting in your `.env`:

```env
LOG_LEVEL=DEBUG
```

## 🔄 Updates and Maintenance

### Regular Maintenance

- **Monitor logs** for errors and connection issues
- **Update dependencies** regularly with `pip install -r requirements.txt --upgrade`
- **Check Pocket Option** for API changes or maintenance
- **Backup configuration** and trade history

### Version History

- **v2.0.0** - Pocket Option integration, trading commands
- **v1.0.0** - Basic utility bot with calculator, jokes, etc.

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## 📄 License

This project is for educational purposes. Use at your own risk.

## 🆘 Support

- **Documentation**: Check this README first
- **Issues**: Create a GitHub issue for bugs
- **Questions**: Check the troubleshooting section
- **Trading Help**: Contact Pocket Option support

## 🎯 Roadmap

- [ ] **Price Charts** - Real-time price charts in Telegram
- [ ] **Technical Indicators** - RSI, MACD, Bollinger Bands
- [ ] **Automated Strategies** - Set and forget trading strategies
- [ ] **Risk Management** - Stop-loss and take-profit orders
- [ ] **Multi-Account** - Support for multiple Pocket Option accounts
- [ ] **Web Dashboard** - Web interface for advanced management

---

**🚀 Ready to start trading? Run `/start` in your bot to get started!**
