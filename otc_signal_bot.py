"""
otc_signal_bot.py
Blueprint: compute RSI + Stochastic + Keltner, send signals to Telegram.
Replace get_candles(...) with real Pocket Option candle feed.
"""

import time
import threading
from typing import List, Dict
import pandas as pd
import pandas_ta as ta
from telegram import Bot

# ========== CONFIG ==========
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"   # from BotFather
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"            # your user id or group id
PAIRS = ["EURUSD-OTC", "USDJPY-OTC"]         # replace with Pocket Option pair names you use
CANDLE_TIMEFRAME = "1m"                      # timeframe for candles
CANDLES_N = 100                              # how many candles to compute indicators on
POLL_INTERVAL = 30                           # seconds between checks per pair (reduced for live trading)
# Debounce: don't resend same signal for same pair within this window (seconds)
SIGNAL_DEBOUNCE_SECONDS = 60 * 3  # 3 minutes (reduced for more frequent signals)
# Auto-restart on errors
MAX_CONSECUTIVE_ERRORS = 5
ERROR_COOLDOWN = 60  # seconds to wait after multiple errors

bot = Bot(token=TELEGRAM_TOKEN)

# Keep last signal timestamps to avoid spamming
last_signal_ts: Dict[str, float] = {}

# ========== Replace this with PocketOption data feed ==========
def get_candles(pair: str, timeframe: str, n: int) -> pd.DataFrame:
    """
    Return a pandas.DataFrame indexed by datetime with columns: ['open','high','low','close','volume'].
    IMPORTANT: Implement this function to fetch real candle data from Pocket Option's feed (or another source).
    For testing you can return synthetic or CSV-based data.
    """
    # --- MOCK data for testing: simple random walk (REMOVE in production) ---
    # Use a deterministic seed if needed
    import numpy as np
    rng = pd.date_range(end=pd.Timestamp.utcnow(), periods=n, freq='1T')
    price = 1.10 + 0.001 * (np.cumsum(np.random.randn(n)) / 10.0)
    df = pd.DataFrame(index=rng)
    df["open"] = price
    df["high"] = price + 0.0005
    df["low"] = price - 0.0005
    df["close"] = price + 0.0001 * np.random.randn(n)
    df["volume"] = 1000 + (np.abs(np.random.randn(n)) * 10).astype(int)
    return df

# ========== Indicator & signal logic ==========
def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds indicators to df and returns it.
    - RSI(14)
    - Stochastic Fast: %K(14,3), %D(3)
    - Keltner Channel: typical length 20 + ATR(10) multiplier 1.5
    """
    df = df.copy()
    # RSI
    df["rsi14"] = ta.rsi(df["close"], length=14)

    # Stochastic Fast (%K and %D)
    stoch = ta.stoch(high=df["high"], low=df["low"], close=df["close"], k=14, d=3)
    # pandas_ta returns columns like STOCHk_14_3_3 etc; we'll assign from returned df
    if isinstance(stoch, pd.DataFrame):
        # find first two columns for %K and %D
        cols = list(stoch.columns)
        if len(cols) >= 2:
            df["stoch_k"] = stoch[cols[0]]
            df["stoch_d"] = stoch[cols[1]]

    # Keltner Channel: center = EMA(20); upper/lower = EMA + / - ATR*mult
    ema_len = 20
    atr_len = 10
    mult = 1.5
    df["ema20"] = ta.ema(df["close"], length=ema_len)
    df["atr10"] = ta.atr(df["high"], df["low"], df["close"], length=atr_len)
    df["keltner_upper"] = df["ema20"] + mult * df["atr10"]
    df["keltner_lower"] = df["ema20"] - mult * df["atr10"]

    return df

def check_signal(df: pd.DataFrame) -> Dict:
    """
    Returns dict with signal: {'side': 'buy'|'sell'|'none', 'reasons': [...]}.
    Oversold (buy) criteria example:
      - RSI < 30
      - stoch_k < 20 and stoch_k < stoch_d (stoch falling)
      - price below lower keltner (close < keltner_lower)
    Overbought (sell) criteria symmetrical:
      - RSI > 70
      - stoch_k > 80 and stoch_k > stoch_d
      - close > keltner_upper
    Use last candle for check.
    """
    res = {"side": "none", "reasons": []}
    last = df.iloc[-1]
    # Must have non-nan indicators
    if pd.isna(last.get("rsi14")) or pd.isna(last.get("stoch_k")) or pd.isna(last.get("keltner_lower")):
        return res

    # Oversold -> BUY signal
    buy_cond = (
        (last["rsi14"] < 30) and
        (last["stoch_k"] < 20) and
        (last["stoch_k"] < last["stoch_d"]) and
        (last["close"] < last["keltner_lower"])
    )

    # Overbought -> SELL signal
    sell_cond = (
        (last["rsi14"] > 70) and
        (last["stoch_k"] > 80) and
        (last["stoch_k"] > last["stoch_d"]) and
        (last["close"] > last["keltner_upper"])
    )

    if buy_cond:
        res["side"] = "buy"
        res["reasons"] = [
            f"RSI={last['rsi14']:.2f} <30",
            f"StochK={last['stoch_k']:.2f} (< StochD={last['stoch_d']:.2f})",
            f"Close {last['close']:.5f} < KeltnerLower {last['keltner_lower']:.5f}"
        ]
    elif sell_cond:
        res["side"] = "sell"
        res["reasons"] = [
            f"RSI={last['rsi14']:.2f} >70",
            f"StochK={last['stoch_k']:.2f} (> StochD={last['stoch_d']:.2f})",
            f"Close {last['close']:.5f} > KeltnerUpper {last['keltner_upper']:.5f}"
        ]

    return res

# ========== Telegram send ==========
def send_telegram_message(text: str):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode="HTML")
        return True
    except Exception as e:
        # handle network / token errors
        print(f"Telegram send error: {e}")
        return False

def send_startup_notification():
    """Send notification when bot starts up"""
    startup_message = f"""
🤖 <b>OTC Signal Bot Started</b>

⏰ <b>Start Time:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 <b>Monitoring Pairs:</b> {', '.join(PAIRS)}
⏱️ <b>Check Interval:</b> {POLL_INTERVAL} seconds
🎯 <b>Signal Types:</b> Enhanced (FVG+Breakout+Technical) + Regular

🚨 <b>Enhanced Signals:</b> FVG + Breakout + Technical indicators
📊 <b>Regular Signals:</b> Technical indicators only

⚠️ <i>Bot is now running and will send signals automatically</i>
"""
    send_telegram_message(startup_message)

# ========== Pair worker ==========
def pair_worker(pair: str):
    """
    Worker thread that continuously monitors a specific pair for signals.
    Runs in its own thread to handle multiple pairs concurrently.
    """
    print(f"Starting worker for {pair}")
    consecutive_errors = 0
    
    while True:
        try:
            # Get latest candles
            df = get_candles(pair, "1m", 150)
            
            # Compute indicators
            df = compute_indicators(df)
            
            # Detect FVG (Fair Value Gap)
            df['bullish_fvg'] = (df['low'] > df['high'].shift(2))
            df['bearish_fvg'] = (df['high'] < df['low'].shift(2))
            
            # Detect breakout
            recent_high = df['high'].iloc[-20:-1].max()
            recent_low = df['low'].iloc[-20:-1].min()
            breakout_up = df['close'].iloc[-1] > recent_high
            breakout_down = df['close'].iloc[-1] < recent_low
            
            # Check oversold/overbought
            sig = check_signal(df)  # from our earlier code
            
            # Combine conditions for enhanced signals
            if breakout_up and df['bullish_fvg'].iloc[-1] and sig['side'] == 'buy':
                # Enhanced BUY signal with FVG and breakout
                current_time = time.time()
                signal_key = f"{pair}_enhanced_buy"
                
                if (signal_key not in last_signal_ts or 
                    current_time - last_signal_ts[signal_key] > SIGNAL_DEBOUNCE_SECONDS):
                    
                    # Format enhanced message
                    message = f"""
🚨 <b>ENHANCED BUY Signal: {pair}</b>

📊 <b>Signal Type:</b> BUY (FVG + Breakout + Technical)
⏰ <b>Time:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
💰 <b>Price:</b> {df['close'].iloc[-1]:.5f}
📈 <b>Breakout Level:</b> {recent_high:.5f}

📊 <b>Technical Indicators:</b>
• RSI: {df['rsi14'].iloc[-1]:.2f}
• Stoch %K: {df['stoch_k'].iloc[-1]:.2f}
• Stoch %D: {df['stoch_d'].iloc[-1]:.2f}
• EMA(20): {df['ema20'].iloc[-1]:.5f}

🔍 <b>Signal Reasons:</b>
• Bullish FVG detected
• Price broke above recent high: {recent_high:.5f}
{chr(10).join(['• ' + reason for reason in sig['reasons']])}

⚠️ <i>This is not financial advice. Always do your own analysis.</i>
"""
                    
                    if send_telegram_message(message):
                        last_signal_ts[signal_key] = current_time
                        print(f"Enhanced BUY signal sent for {pair}")
                        consecutive_errors = 0  # Reset error counter on successful signal
                    
            elif breakout_down and df['bearish_fvg'].iloc[-1] and sig['side'] == 'sell':
                # Enhanced SELL signal with FVG and breakout
                current_time = time.time()
                signal_key = f"{pair}_enhanced_sell"
                
                if (signal_key not in last_signal_ts or 
                    current_time - last_signal_ts[signal_key] > SIGNAL_DEBOUNCE_SECONDS):
                    
                    # Format enhanced message
                    message = f"""
🚨 <b>ENHANCED SELL Signal: {pair}</b>

📊 <b>Signal Type:</b> SELL (FVG + Breakout + Technical)
⏰ <b>Time:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
💰 <b>Price:</b> {df['close'].iloc[-1]:.5f}
📉 <b>Breakout Level:</b> {recent_low:.5f}

📊 <b>Technical Indicators:</b>
• RSI: {df['rsi14'].iloc[-1]:.2f}
• Stoch %K: {df['stoch_k'].iloc[-1]:.2f}
• Stoch %D: {df['stoch_d'].iloc[-1]:.2f}
• EMA(20): {df['ema20'].iloc[-1]:.5f}

🔍 <b>Signal Reasons:</b>
• Bearish FVG detected
• Price broke below recent low: {recent_low:.5f}
{chr(10).join(['• ' + reason for reason in sig['reasons']])}

⚠️ <i>This is not financial advice. Always do your own analysis.</i>
"""
                    
                    if send_telegram_message(message):
                        last_signal_ts[signal_key] = current_time
                        print(f"Enhanced SELL signal sent for {pair}")
                        consecutive_errors = 0  # Reset error counter on successful signal
            
            # Also check for regular signals (without FVG/breakout) as backup
            elif sig["side"] != "none":
                current_time = time.time()
                
                # Check debounce - don't send same signal type too frequently
                signal_key = f"{pair}_{sig['side']}"
                if (signal_key not in last_signal_ts or 
                    current_time - last_signal_ts[signal_key] > SIGNAL_DEBOUNCE_SECONDS):
                    
                    # Format regular message
                    message = f"""
📊 <b>Regular Signal: {pair}</b>

📊 <b>Signal:</b> {sig['side'].upper()}
⏰ <b>Time:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
💰 <b>Price:</b> {df.iloc[-1]['close']:.5f}

📈 <b>Indicators:</b>
• RSI: {df.iloc[-1]['rsi14']:.2f}
• Stoch %K: {df.iloc[-1]['stoch_k']:.2f}
• Stoch %D: {df.iloc[-1]['stoch_d']:.2f}
• EMA(20): {df.iloc[-1]['ema20']:.5f}

🔍 <b>Reasons:</b>
{chr(10).join(['• ' + reason for reason in sig['reasons']])}

⚠️ <i>This is not financial advice. Always do your own analysis.</i>
"""
                    
                    # Send to Telegram
                    if send_telegram_message(message):
                        last_signal_ts[signal_key] = current_time
                        print(f"Regular signal sent for {pair}: {sig['side']}")
                        consecutive_errors = 0  # Reset error counter on successful signal
            
            # Wait before next check
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            consecutive_errors += 1
            print(f"Error in {pair} worker (attempt {consecutive_errors}): {e}")
            
            # If too many consecutive errors, wait longer
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print(f"Too many errors for {pair}, waiting {ERROR_COOLDOWN} seconds...")
                time.sleep(ERROR_COOLDOWN)
                consecutive_errors = 0  # Reset counter
            else:
                time.sleep(POLL_INTERVAL)

# ========== Main execution ==========
def main():
    """
    Main function that starts worker threads for each pair.
    """
    print("Starting OTC Signal Bot...")
    print(f"Monitoring pairs: {PAIRS}")
    print(f"Timeframe: {CANDLE_TIMEFRAME}")
    print(f"Poll interval: {POLL_INTERVAL} seconds")
    print(f"Signal debounce: {SIGNAL_DEBOUNCE_SECONDS} seconds")
    
    # Send startup notification to Telegram
    print("Sending startup notification...")
    send_startup_notification()
    
    # Start worker thread for each pair
    threads = []
    for pair in PAIRS:
        thread = threading.Thread(target=pair_worker, args=(pair,), daemon=True)
        thread.start()
        threads.append(thread)
        print(f"Started thread for {pair}")
    
    print("All workers started. Bot is now running automatically...")
    print("Press Ctrl+C to stop the bot")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        # Send shutdown notification
        shutdown_message = f"""
🛑 <b>OTC Signal Bot Stopped</b>

⏰ <b>Stop Time:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
⚠️ <i>Bot is no longer monitoring for signals</i>
"""
        send_telegram_message(shutdown_message)
        # Threads are daemon, so they'll exit when main thread exits

if __name__ == "__main__":
    main()
