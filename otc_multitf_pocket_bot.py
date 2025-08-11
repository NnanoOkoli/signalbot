#!/usr/bin/env python3
"""
Integrated Multi-Timeframe OTC Signal Bot with Pocket Option API
Combines advanced technical analysis with real market data
"""
import asyncio
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple
import pandas as pd
import ta
import numpy as np
import aiohttp
import math
import logging
import os
import sys

# Import Pocket Option API
try:
    from pocket_option_api import PocketOptionAPI
except ImportError:
    print("Error: pocket_option_api.py not found. Make sure it's in the same directory.")
    sys.exit(1)

# Import configuration
try:
    from config import *
except ImportError:
    print("Error: config.py not found. Please copy config_multitf_template.py to config.py and configure it.")
    sys.exit(1)

# ========== Data structures ==========
@dataclass
class Candle:
    ts: float
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

@dataclass
class FVGap:
    pair: str
    tf: str
    side: str  # 'bull' or 'bear'
    top: float
    bottom: float
    created_at: float = field(default_factory=time.time)
    filled: bool = False

@dataclass
class SRZone:
    pair: str
    low: float
    high: float
    strength: int = 1
    last_touched: float = field(default_factory=time.time)

# ========== Global storage ==========
buffers: Dict[str, Dict[str, Deque[Candle]]] = defaultdict(lambda: {tf: deque(maxlen=CANDLES_N) for tf in TF_DEFS})
fvg_store: Dict[str, List[FVGap]] = defaultdict(list)
sr_store: Dict[str, List[SRZone]] = defaultdict(list)
last_signal_ts: Dict[str, float] = defaultdict(lambda: 0.0)

# ========== Pocket Option API instance ==========
pocket_api = None

# ========== Setup logging ==========
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("otc_pocket_bot")

# ========== Utility functions ==========
def candles_to_df(candles: Deque[Candle]) -> pd.DataFrame:
    """Convert deque of candles to pandas DataFrame"""
    if len(candles) == 0:
        return pd.DataFrame()
    
    arr = [{
        "ts": c.ts,
        "open": c.open,
        "high": c.high,
        "low": c.low,
        "close": c.close,
        "volume": c.volume
    } for c in candles]
    
    df = pd.DataFrame(arr).set_index(pd.to_datetime([c["ts"] for c in arr], unit="s"))
    return df

async def send_telegram(text: str):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    txt = await resp.text()
                    logger.warning("Telegram send failed %s %s", resp.status, txt)
                else:
                    logger.info("Telegram message sent successfully")
    except Exception as e:
        logger.exception("Telegram error: %s", e)

# ========== Technical Analysis ==========
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators to DataFrame"""
    if df.empty or len(df) < max(EMA_LEN, ATR_LEN, 14):
        return df
    
    df = df.copy()
    
    # RSI
    df["rsi14"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    
    # Stochastic
    stoch = ta.momentum.StochasticOscillator(df["high"], df["low"], df["close"], window=14, smooth_window=3)
    df["stoch_k"] = stoch.stoch()
    df["stoch_d"] = stoch.stoch_signal()
    
    # Keltner Channels
    df["ema20"] = ta.trend.EMAIndicator(df["close"], window=EMA_LEN).ema_indicator()
    df["atr10"] = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"], window=ATR_LEN).average_true_range()
    df["keltner_upper"] = df["ema20"] + KC_MULT * df["atr10"]
    df["keltner_lower"] = df["ema20"] - KC_MULT * df["atr10"]
    
    return df

def detect_fvg_for_df(pair: str, tf: str, df: pd.DataFrame) -> List[FVGap]:
    """Detect Fair Value Gaps in DataFrame"""
    gaps: List[FVGap] = []
    
    if df.shape[0] < 3:
        return gaps
    
    # Find indices where gap exists
    for i in range(2, min(len(df), 50)):
        row = df.iloc[-i]
        row_m2 = df.iloc[-i-2]
        
        # Bullish gap: low[i] > high[i-2]
        if row["low"] > row_m2["high"]:
            top = float(row_m2["high"])
            bottom = float(row["low"])
            gaps.append(FVGap(pair=pair, tf=tf, side="bull", top=top, bottom=bottom))
        
        # Bearish gap: high[i] < low[i-2]
        elif row["high"] < row_m2["low"]:
            top = float(row["high"])
            bottom = float(row_m2["low"])
            gaps.append(FVGap(pair=pair, tf=tf, side="bear", top=top, bottom=bottom))
    
    return gaps

def update_fvg_store(pair: str, tf: str, df: pd.DataFrame):
    """Update FVG store with new gaps"""
    new = detect_fvg_for_df(pair, tf, df)
    existing = fvg_store[pair]
    
    # Deduplicate by top/bottom within epsilon
    eps = 1e-6
    for g in new:
        if not any(abs(g.top - e.top) < eps and abs(g.bottom - e.bottom) < eps for e in existing):
            existing.append(g)
            logger.info("New FVG %s %s %s->%s", pair, tf, g.side, (g.top, g.bottom))

def expire_and_fill_fvgs(pair: str, current_price: float):
    """Mark FVGs as filled if price enters zone"""
    for gap in fvg_store[pair]:
        if not gap.filled:
            if gap.side == "bull" and current_price >= gap.bottom:
                gap.filled = True
                logger.info("FVG filled %s %s bull", pair, gap.tf)
            elif gap.side == "bear" and current_price <= gap.top:
                gap.filled = True
                logger.info("FVG filled %s %s bear", pair, gap.tf)

def detect_swing_points(df: pd.DataFrame, lookback=3) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """Detect swing highs and lows"""
    highs, lows = [], []
    
    for i in range(lookback, len(df) - lookback):
        # Swing high
        if all(df.iloc[i]["high"] > df.iloc[j]["high"] for j in range(i-lookback, i+lookback+1) if j != i):
            highs.append((i, df.iloc[i]["high"]))
        
        # Swing low
        if all(df.iloc[i]["low"] < df.iloc[j]["low"] for j in range(i-lookback, i+lookback+1) if j != i):
            lows.append((i, df.iloc[i]["low"]))
    
    return highs, lows

def cluster_sr_zones(pair: str, df: pd.DataFrame, tol=0.003):
    """Cluster swing points into support/resistance zones"""
    highs, lows = detect_swing_points(df)
    
    # Cluster highs (resistance)
    for idx, high in highs:
        found_zone = False
        for zone in sr_store[pair]:
            if abs(zone.high - high) < tol:
                zone.high = max(zone.high, high)
                zone.strength += 1
                zone.last_touched = time.time()
                found_zone = True
                break
        
        if not found_zone:
            sr_store[pair].append(SRZone(pair=pair, low=high-tol, high=high+tol))
    
    # Cluster lows (support)
    for idx, low in lows:
        found_zone = False
        for zone in sr_store[pair]:
            if abs(zone.low - low) < tol:
                zone.low = min(zone.low, low)
                zone.strength += 1
                zone.last_touched = time.time()
                found_zone = True
                break
        
        if not found_zone:
            sr_store[pair].append(SRZone(pair=pair, low=low-tol, high=low+tol))

def is_breakout(df: pd.DataFrame, direction: str, range_bars=HTF_RANGE_BARS) -> bool:
    """Detect breakout patterns"""
    if len(df) < range_bars:
        return False
    
    recent_high = df.iloc[-range_bars:-1]["high"].max()
    recent_low = df.iloc[-range_bars:-1]["low"].min()
    
    if direction == "up":
        breakout_price = recent_high
        current_price = df.iloc[-1]["close"]
        body = abs(df.iloc[-1]["close"] - df.iloc[-1]["open"])
        range_size = recent_high - recent_low
        
        return (current_price > breakout_price and 
                body >= range_size * BREAKOUT_BODY_RATIO)
    
    elif direction == "down":
        breakout_price = recent_low
        current_price = df.iloc[-1]["close"]
        body = abs(df.iloc[-1]["close"] - df.iloc[-1]["open"])
        range_size = recent_high - recent_low
        
        return (current_price < breakout_price and 
                body >= range_size * BREAKOUT_BODY_RATIO)
    
    return False

def compute_score(pair: str, df_htf: pd.DataFrame, df_mtf: pd.DataFrame, df_ltf: pd.DataFrame) -> Tuple[str, List[str], int]:
    """Compute signal score based on multiple timeframes"""
    if df_htf.empty or df_mtf.empty or df_ltf.empty:
        return "none", [], 0
    
    reasons = []
    score = 0
    
    # HTF trend analysis
    if not df_htf.empty:
        last_htf = df_htf.iloc[-1]
        if pd.notna(last_htf.get("rsi14")):
            if last_htf["rsi14"] < 30:
                score += 20
                reasons.append("HTF: RSI oversold")
            elif last_htf["rsi14"] > 70:
                score -= 20
                reasons.append("HTF: RSI overbought")
    
    # MTF signal analysis
    if not df_mtf.empty:
        last_mtf = df_mtf.iloc[-1]
        
        # RSI conditions
        if pd.notna(last_mtf.get("rsi14")):
            if last_mtf["rsi14"] < 30:
                score += 15
                reasons.append("MTF: RSI oversold")
            elif last_mtf["rsi14"] > 70:
                score -= 15
                reasons.append("MTF: RSI overbought")
        
        # Stochastic conditions
        if pd.notna(last_mtf.get("stoch_k")) and pd.notna(last_mtf.get("stoch_d")):
            if last_mtf["stoch_k"] < 20 and last_mtf["stoch_k"] < last_mtf["stoch_d"]:
                score += 10
                reasons.append("MTF: Stochastic oversold")
            elif last_mtf["stoch_k"] > 80 and last_mtf["stoch_k"] > last_mtf["stoch_d"]:
                score -= 10
                reasons.append("MTF: Stochastic overbought")
        
        # Keltner Channel conditions
        if pd.notna(last_mtf.get("keltner_lower")) and pd.notna(last_mtf.get("keltner_upper")):
            if last_mtf["close"] < last_mtf["keltner_lower"]:
                score += 10
                reasons.append("MTF: Price below Keltner lower")
            elif last_mtf["close"] > last_mtf["keltner_upper"]:
                score -= 10
                reasons.append("MTF: Price above Keltner upper")
    
    # LTF refinement
    if not df_ltf.empty:
        last_ltf = df_ltf.iloc[-1]
        if pd.notna(last_ltf.get("rsi14")):
            if last_ltf["rsi14"] < 40:
                score += 5
                reasons.append("LTF: RSI supportive")
            elif last_ltf["rsi14"] > 60:
                score -= 5
                reasons.append("LTF: RSI resistive")
    
    # FVG analysis
    for gap in fvg_store[pair]:
        if not gap.filled:
            if gap.side == "bull" and df_mtf.iloc[-1]["close"] < gap.bottom:
                score += 8
                reasons.append("FVG: Bullish gap above")
            elif gap.side == "bear" and df_mtf.iloc[-1]["close"] > gap.top:
                score -= 8
                reasons.append("FVG: Bearish gap below")
    
    # Breakout analysis
    if is_breakout(df_mtf, "up"):
        score += 12
        reasons.append("Breakout: Upward breakout detected")
    elif is_breakout(df_mtf, "down"):
        score -= 12
        reasons.append("Breakout: Downward breakout detected")
    
    # Determine signal side
    if score >= 25:
        return "buy", reasons, score
    elif score <= -25:
        return "sell", reasons, score
    else:
        return "none", reasons, score

# ========== Pocket Option Integration ==========
async def initialize_pocket_api():
    """Initialize Pocket Option API connection"""
    global pocket_api
    
    try:
        # Create Pocket Option API instance
        pocket_api = PocketOptionAPI(type('Config', (), {
            'POCKET_OPTION_EMAIL': POCKET_OPTION_EMAIL,
            'POCKET_OPTION_PASSWORD': POCKET_OPTION_PASSWORD
        })())
        
        # Authenticate
        if pocket_api.authenticate():
            logger.info("Successfully authenticated with Pocket Option")
            
            # Connect WebSocket for real-time data
            pocket_api.connect_websocket()
            await asyncio.sleep(2)  # Wait for connection
            
            return True
        else:
            logger.error("Failed to authenticate with Pocket Option")
            return False
            
    except Exception as e:
        logger.exception("Error initializing Pocket Option API: %s", e)
        return False

async def get_live_candles(pair: str) -> List[Tuple[str, Candle]]:
    """Get live candles from Pocket Option API"""
    global pocket_api
    
    if not pocket_api or not pocket_api.is_authenticated:
        logger.warning("Pocket Option API not initialized, using stub data")
        return await get_live_candles_stub(pair)
    
    try:
        candles_out = []
        now = time.time()
        
        # Get data for each timeframe
        for tf in TF_DEFS:
            try:
                # Get market data from Pocket Option
                market_data = pocket_api.get_market_data(pair, tf, 1)
                
                if market_data and 'candles' in market_data:
                    candle_data = market_data['candles'][0] if market_data['candles'] else None
                    
                    if candle_data:
                        candle = Candle(
                            ts=now,
                            open=float(candle_data['open']),
                            high=float(candle_data['high']),
                            low=float(candle_data['low']),
                            close=float(candle_data['close']),
                            volume=float(candle_data.get('volume', 100))
                        )
                        candles_out.append((tf, candle))
                
            except Exception as e:
                logger.warning("Error getting %s data for %s: %s", tf, pair, e)
                continue
        
        # If no real data, fall back to stub
        if not candles_out:
            logger.info("No real data available, using stub data")
            return await get_live_candles_stub(pair)
        
        return candles_out
        
    except Exception as e:
        logger.exception("Error getting live candles: %s", e)
        return await get_live_candles_stub(pair)

async def get_live_candles_stub(pair: str) -> List[Tuple[str, Candle]]:
    """Fallback stub data generator"""
    now = time.time()
    base = 1.1000 + 0.001 * math.sin(now / 37.0 + hash(pair) % 10)
    jitter = (np.random.randn() * 0.0002)
    price = base + jitter
    
    candles_out = []
    
    # Create 30s candle
    c30 = Candle(ts=now, open=price-0.0001, high=price+0.0002, low=price-0.0002, close=price, volume=100)
    candles_out.append(("30s", c30))
    
    # Aggregate to higher timeframes
    if int(now) % 60 < 2:
        c1 = Candle(ts=now, open=price-0.0003, high=price+0.0004, low=price-0.0004, close=price, volume=240)
        candles_out.append(("1m", c1))
    
    if int(now) % 180 < 3:
        c3 = Candle(ts=now, open=price-0.0005, high=price+0.0008, low=price-0.0007, close=price, volume=600)
        candles_out.append(("3m", c3))
    
    if int(now) % 300 < 3:
        c5 = Candle(ts=now, open=price-0.0009, high=price+0.0012, low=price-0.0011, close=price, volume=1200)
        candles_out.append(("5m", c5))
    
    return candles_out

# ========== Main worker ==========
async def pair_worker(pair: str):
    """Main worker for each trading pair"""
    logger.info("Starting worker for %s", pair)
    
    while True:
        try:
            # Get new candles
            new_candles = await get_live_candles(pair)
            
            # Process each timeframe
            for tf, candle in new_candles:
                if tf in TF_DEFS:
                    buffers[pair][tf].append(candle)
                    
                    # Add indicators when we have enough data
                    if len(buffers[pair][tf]) >= 50:
                        df = candles_to_df(buffers[pair][tf])
                        df = add_indicators(df)
                        
                        # Detect FVGs on MTF
                        if tf == MTF:
                            update_fvg_store(pair, tf, df)
                        
                        # Detect SR zones
                        if len(df) >= 50:
                            cluster_sr_zones(pair, df)
            
            # Expire FVGs using latest price
            latest_price = None
            if buffers[pair][MTF]:
                latest_price = buffers[pair][MTF][-1].close
            elif buffers[pair][LTF]:
                latest_price = buffers[pair][LTF][-1].close
            
            if latest_price:
                expire_and_fill_fvgs(pair, latest_price)
            
            # Compute signal using all timeframes
            df_htf = add_indicators(candles_to_df(buffers[pair][HTF]))
            df_mtf = add_indicators(candles_to_df(buffers[pair][MTF]))
            df_ltf = add_indicators(candles_to_df(buffers[pair][LTF]))
            
            side, reasons, score = compute_score(pair, df_htf, df_mtf, df_ltf)
            
            now = time.time()
            if side != "none" and (now - last_signal_ts[pair]) > SIGNAL_DEBOUNCE:
                # Build signal message
                txt = f"🔔 <b>{pair}</b> SIGNAL: <b>{side.upper()}</b>\n"
                txt += f"Score: {score}\n"
                txt += f"Timeframe: {HTF} + {MTF} + {LTF}\n\n"
                
                for r in reasons:
                    txt += f"• {r}\n"
                
                if not df_mtf.empty:
                    txt += f"\n💰 Price: {df_mtf.iloc[-1]['close']:.5f}"
                    txt += f"\n⏰ Time: {df_mtf.index[-1].strftime('%H:%M:%S')} UTC"
                
                await send_telegram(txt)
                last_signal_ts[pair] = now
                logger.info("Sent signal %s %s (score=%d)", pair, side, score)
            
            await asyncio.sleep(POLL_INTERVAL)
            
        except Exception as e:
            logger.exception("Error in pair_worker %s: %s", pair, e)
            await asyncio.sleep(1.0)

# ========== Main function ==========
async def main():
    """Main function"""
    logger.info("Starting Integrated Multi-Timeframe OTC Signal Bot with Pocket Option API")
    
    # Initialize Pocket Option API
    if not await initialize_pocket_api():
        logger.warning("Continuing with stub data - Pocket Option API not available")
    
    # Send startup notification
    startup_msg = f"""
🚀 <b>OTC Signal Bot Started</b>

📊 <b>Multi-Timeframe Analysis:</b>
• High TF: {HTF}
• Medium TF: {MTF} 
• Low TF: {LTF}

📈 <b>Pairs:</b> {', '.join(PAIRS)}
⏰ <b>Start Time:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 <b>Mode:</b> {'Real Data' if pocket_api and pocket_api.is_authenticated else 'Stub Data'}
    """
    
    await send_telegram(startup_msg)
    
    # Start worker tasks for each pair
    tasks = []
    for pair in PAIRS:
        task = asyncio.create_task(pair_worker(pair))
        tasks.append(task)
        await asyncio.sleep(0.2)
    
    logger.info("Workers started for pairs: %s", PAIRS)
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    finally:
        # Send shutdown notification
        shutdown_msg = f"""
🛑 <b>OTC Signal Bot Stopped</b>

⏰ <b>Stop Time:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
⚠️ <i>Bot is no longer monitoring for signals</i>
        """
        await send_telegram(shutdown_msg)
        
        # Disconnect Pocket Option API
        if pocket_api:
            pocket_api.disconnect_websocket()
            pocket_api.logout()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        sys.exit(1)
