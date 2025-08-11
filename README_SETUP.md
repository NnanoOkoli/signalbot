# 🚀 OTC Signal Bot - Setup Guide

## 📋 Overview

This bot automatically monitors OTC trading pairs for technical signals and sends them directly to your Telegram chat. It combines:

- **RSI + Stochastic + Keltner Channel** indicators
- **Fair Value Gap (FVG)** detection
- **Breakout** detection
- **Enhanced signal combinations** for higher probability setups

## 🛠️ Quick Setup

### 1. Install Required Packages

```bash
pip install python-telegram-bot==13.15 pandas pandas_ta websocket-client numpy
```

### 2. Create Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Choose a name for your bot
4. Choose a username (must end in 'bot')
5. **Save the bot token** - you'll need this!

### 3. Get Your Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send any message
3. **Save your chat ID** - you'll need this!

### 4. Configure the Bot

1. Copy `config_template.py` to `config.py`
2. Edit `config.py` with your actual values:
   ```python
   TELEGRAM_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"  # Your bot token
   TELEGRAM_CHAT_ID = "123456789"                              # Your chat ID
   PAIRS = ["EURUSD-OTC", "GBPUSD-OTC"]                       # Your trading pairs
   ```

### 5. Run the Bot

```bash
python start_bot.py
```

## 📱 What You'll Receive

### 🚨 Enhanced Signals (Highest Priority)

- **FVG + Breakout + Technical indicators** aligned
- Marked with 🚨 emoji
- Includes breakout levels and detailed analysis

### 📊 Regular Signals

- **Technical indicators only** (RSI, Stochastic, Keltner)
- Marked with 📊 emoji
- Backup signals when enhanced conditions aren't met

### 🤖 Bot Status Messages

- **Startup notification** when bot begins
- **Shutdown notification** when bot stops
- **Error handling** with automatic recovery

## ⚙️ Configuration Options

| Setting                   | Default    | Description                    |
| ------------------------- | ---------- | ------------------------------ |
| `POLL_INTERVAL`           | 30 seconds | How often to check each pair   |
| `SIGNAL_DEBOUNCE_SECONDS` | 3 minutes  | Time between same signal types |
| `MAX_CONSECUTIVE_ERRORS`  | 5          | Errors before cooldown         |
| `ERROR_COOLDOWN`          | 60 seconds | Wait time after errors         |

## 🔄 Automatic Operation

The bot runs **continuously** and **automatically**:

- ✅ **No manual intervention** needed
- ✅ **Automatic error recovery**
- ✅ **Restart capability** with `start_bot.py`
- ✅ **Real-time monitoring** 24/7
- ✅ **Smart debouncing** prevents signal spam

## 🚨 Signal Types

### Enhanced BUY Signal

- Price breaks above recent high
- Bullish FVG detected
- RSI oversold + Stochastic oversold + Price below Keltner lower

### Enhanced SELL Signal

- Price breaks below recent low
- Bearish FVG detected
- RSI overbought + Stochastic overbought + Price above Keltner upper

### Regular Signals

- Standard technical indicator conditions
- Sent when enhanced conditions aren't met

## 🛡️ Safety Features

- **Debouncing**: Prevents duplicate signals
- **Error handling**: Automatic recovery from failures
- **Cooldown periods**: Prevents excessive restarts
- **Graceful shutdown**: Sends notification when stopping

## 📊 Current Status

The bot will send you a **startup message** when it begins running, showing:

- ✅ All monitored pairs
- ✅ Check intervals
- ✅ Signal types enabled
- ✅ Current status

## 🚀 Next Steps

1. **Test with mock data** (already included)
2. **Replace `get_candles()`** with real Pocket Option API
3. **Customize signal parameters** in `config.py`
4. **Add more trading pairs** as needed
5. **Deploy to server** for 24/7 operation

## ⚠️ Important Notes

- **This is not financial advice** - always do your own analysis
- **Test thoroughly** before using with real money
- **Monitor the bot** for any errors or issues
- **Keep your bot token secure** - don't share it publicly

## 🆘 Troubleshooting

### Bot won't start

- Check Python packages are installed
- Verify Telegram token and chat ID
- Check file permissions

### No signals received

- Verify bot is running (check console output)
- Check Telegram bot is added to your chat
- Verify chat ID is correct

### Too many errors

- Check internet connection
- Verify Pocket Option API access
- Check error logs in console

---

**Happy Trading! 🎯📈**
