# 🚀 Integrated Multi-Timeframe OTC Signal Bot with Pocket Option API

## 🎯 **What This Bot Does**

This is a **professional-grade trading signal bot** that combines:

- **Multi-timeframe technical analysis** (30s, 1m, 3m, 5m)
- **Real-time market data** from Pocket Option API
- **Advanced pattern recognition** (FVG, Breakouts, Support/Resistance)
- **Intelligent scoring system** for high-quality signals
- **Telegram notifications** with detailed analysis

## 🔧 **Features**

### **📊 Multi-Timeframe Analysis**

- **High Timeframe (5m)**: Trend direction and major levels
- **Medium Timeframe (1m)**: Signal generation and pattern detection
- **Low Timeframe (30s)**: Entry refinement and timing

### **🎯 Advanced Signal Detection**

- **RSI + Stochastic + Keltner Channels** combination
- **Fair Value Gaps (FVG)** detection and tracking
- **Breakout patterns** with volume confirmation
- **Support/Resistance zones** clustering
- **Multi-timeframe scoring** (0-100 scale)

### **📡 Real Market Data**

- **Live Pocket Option API** integration
- **WebSocket connection** for real-time updates
- **Automatic fallback** to synthetic data if API unavailable
- **Multiple timeframe aggregation**

### **🔔 Smart Notifications**

- **Debounced signals** (no spam)
- **Detailed analysis** with reasons
- **Score-based filtering** (only high-quality signals)
- **Startup/shutdown notifications**

## 📋 **Prerequisites**

### **Required Software**

- Python 3.7+
- Git (for cloning)

### **Required Python Packages**

```bash
pip install pandas pandas_ta numpy aiohttp python-telegram-bot==13.15
```

### **Accounts Needed**

1. **Telegram Bot** (get token from @BotFather)
2. **Pocket Option Account** (for real market data)

## 🚀 **Quick Start**

### **Step 1: Get Your Telegram Bot Token**

1. Message @BotFather on Telegram
2. Create a new bot: `/newbot`
3. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### **Step 2: Get Your Chat ID**

1. Message @userinfobot on Telegram
2. Copy your numeric Chat ID

### **Step 3: Configure the Bot**

1. **Copy the config template:**

   ```bash
   cp config_multitf_template.py config.py
   ```

2. **Edit config.py with your credentials:**

   ```python
   TELEGRAM_TOKEN = "YOUR_ACTUAL_BOT_TOKEN_HERE"
   TELEGRAM_CHAT_ID = "YOUR_ACTUAL_CHAT_ID_HERE"

   # Pocket Option credentials
   POCKET_OPTION_EMAIL = "your_email@example.com"
   POCKET_OPTION_PASSWORD = "your_password"
   POCKET_OPTION_DEMO = True  # Set to False for real account
   ```

### **Step 4: Start the Bot**

```bash
python start_pocket_bot.py
```

## 📁 **File Structure**

```
signal bot/
├── otc_multitf_pocket_bot.py    # 🆕 Main integrated bot
├── start_pocket_bot.py          # 🆕 Startup script
├── pocket_option_api.py         # Pocket Option API integration
├── config.py                    # Configuration (update with your credentials)
├── config_multitf_template.py   # Configuration template
├── README_POCKET_INTEGRATION.md # This file
└── ... (other files)
```

## ⚙️ **Configuration Options**

### **Core Settings**

```python
# Trading pairs to monitor
PAIRS = ["EURUSD-OTC", "USDJPY-OTC", "GBPUSD-OTC"]

# Timeframes (in seconds)
TF_DEFS = {
    "30s": 30,    # Low timeframe
    "1m": 60,     # Medium timeframe
    "3m": 180,    # Additional timeframe
    "5m": 300,    # High timeframe
}

# Which timeframes to use for decisions
HTF = "5m"        # High timeframe
MTF = "1m"        # Medium timeframe
LTF = "30s"       # Low timeframe
```

### **Signal Parameters**

```python
CANDLES_N = 200                    # History length per timeframe
POLL_INTERVAL = 1.0                # Seconds between checks
SIGNAL_DEBOUNCE = 60 * 3           # 3 minutes between signals
HTF_RANGE_BARS = 20                # Bars for breakout detection
BREAKOUT_BODY_RATIO = 0.35         # Minimum body size for breakout
```

### **Technical Indicators**

```python
EMA_LEN = 20                       # EMA length for Keltner
ATR_LEN = 10                       # ATR length for volatility
KC_MULT = 1.5                      # Keltner Channel multiplier
```

## 📊 **Signal Types & Examples**

### **🔴 SELL Signal Example**

```
🔔 EURUSD-OTC SIGNAL: SELL
Score: -32
Timeframe: 5m + 1m + 30s

• HTF: RSI overbought
• MTF: RSI overbought
• MTF: Stochastic overbought
• MTF: Price above Keltner upper
• Breakout: Downward breakout detected

💰 Price: 1.08745
⏰ Time: 14:23:45 UTC
```

### **🟢 BUY Signal Example**

```
🔔 USDJPY-OTC SIGNAL: BUY
Score: 28
Timeframe: 5m + 1m + 30s

• HTF: RSI oversold
• MTF: RSI oversold
• MTF: Stochastic oversold
• MTF: Price below Keltner lower
• FVG: Bullish gap above
• LTF: RSI supportive

💰 Price: 148.234
⏰ Time: 14:23:45 UTC
```

## 🔍 **How the Scoring Works**

### **Score Components**

- **HTF Trend**: ±20 points (RSI oversold/overbought)
- **MTF Signals**: ±15 points (RSI, Stochastic, Keltner)
- **LTF Refinement**: ±5 points (RSI support/resistance)
- **FVG Analysis**: ±8 points (unfilled gaps)
- **Breakout Detection**: ±12 points (confirmed breakouts)

### **Signal Thresholds**

- **BUY Signal**: Score ≥ +25
- **SELL Signal**: Score ≤ -25
- **No Signal**: Score between -24 and +24

## 🚨 **Important Notes**

### **Live Data Integration**

- **Real-time**: Uses Pocket Option WebSocket API
- **Fallback**: Automatically switches to synthetic data if API fails
- **Authentication**: Requires valid Pocket Option credentials
- **Demo Mode**: Set `POCKET_OPTION_DEMO = True` for testing

### **Performance & Reliability**

- **Debouncing**: Prevents signal spam (3-minute minimum interval)
- **Error Handling**: Automatic retry and fallback mechanisms
- **Memory Management**: Efficient candle buffer management
- **Async Processing**: Non-blocking operations for smooth operation

### **Risk Management**

- **Signal Quality**: Only high-scoring signals are sent
- **Multi-timeframe Confirmation**: Requires agreement across timeframes
- **Pattern Validation**: FVG and breakout confirmation required
- **No Trading**: This bot only generates signals, doesn't place trades

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **"Pocket Option API not initialized"**

- Check your email/password in `config.py`
- Verify Pocket Option account is active
- Check internet connection

#### **"Telegram send failed"**

- Verify bot token is correct
- Check chat ID is correct
- Ensure bot has permission to send messages

#### **"No signals generated"**

- Check if pairs are correctly configured
- Verify timeframes are valid
- Check if indicators are computing correctly

### **Debug Mode**

Enable detailed logging by modifying the bot:

```python
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
```

## 🔮 **Future Enhancements**

### **Planned Features**

- **More indicators**: MACD, Bollinger Bands, Ichimoku
- **Risk scoring**: Position sizing recommendations
- **Backtesting**: Historical performance analysis
- **Web dashboard**: Real-time monitoring interface
- **Multiple exchanges**: Support for other brokers

### **Customization Options**

- **Custom indicators**: Add your own technical analysis
- **Signal filters**: Adjust sensitivity and thresholds
- **Time-based rules**: Market hours and session filters
- **News integration**: Economic calendar impact

## 📞 **Support & Community**

### **Getting Help**

1. **Check this README** for common solutions
2. **Review logs** for error details
3. **Test with stub data** first
4. **Verify configuration** step by step

### **Best Practices**

- **Start with demo mode** to test functionality
- **Monitor logs** for any errors or warnings
- **Use appropriate timeframes** for your trading style
- **Regularly update** your Pocket Option credentials

## 🎉 **Congratulations!**

You now have a **professional-grade trading signal bot** that combines:

- ✅ **Advanced technical analysis**
- ✅ **Real-time market data**
- ✅ **Intelligent signal filtering**
- ✅ **Professional notifications**

**Next Steps:**

1. **Configure your credentials** in `config.py`
2. **Test with stub data** first
3. **Start the bot** with `python start_pocket_bot.py`
4. **Monitor signals** in Telegram
5. **Customize settings** based on your preferences

**Happy Trading! 🚀📈**
