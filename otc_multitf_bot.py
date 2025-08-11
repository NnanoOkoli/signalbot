"""
otc_multitf_bot.py
Async multi-timeframe OTC signal engine:
- Maintains candle buffers for multiple timeframes
- Computes indicators (RSI, Stochastic, EMA + ATR -> Keltner)
- Detects Fair Value Gaps (FVG), Swing SR zones, Breakouts
- Multi-timeframe scoring and Telegram alerts

IMPORTANT:
- Replace `get_live_candle(pair)` with your Pocket Option websocket / feed.
- Configure TELEGRAM_TOKEN and TELEGRAM_CHAT_ID below.
"""

import asyncio
import time
from collections import deque, defaultdict, namedtuple
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple
import pandas as pd
import pandas_ta as ta
import numpy as np
import aiohttp
import math
import logging

# ---------------- CONFIG ----------------
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # numeric id or group id
PAIRS = ["EURUSD-OTC", "USDJPY-OTC"]  # your symbols

# timeframes (seconds)
TF_DEFS = {
    "30s": 30,
    "1m": 60,
    "3m": 180,
    "5m": 300,
}

# Which TFs to use for decision
HTF = "5m"
MTF = "1m"
LTF = "30s"  # for entry refinement (may be simulated from 1s ticks)

CANDLES_N = 200  # history length per timeframe
POLL_INTERVAL = 1.0  # seconds between polls for new candles
SIGNAL_DEBOUNCE = 60 * 3  # seconds before re-sending same pair signal

# Breakout params
HTF_RANGE_BARS = 20
BREAKOUT_BODY_RATIO = 0.35  # body >= this % of candle range required

# Keltner params
EMA_LEN = 20
ATR_LEN = 10
KC_MULT = 1.5

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("otc_bot")

# ---------------- Data structures ----------------
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

# Per-pair storage
buffers: Dict[str, Dict[str, Deque[Candle]]] = defaultdict(lambda: {tf: deque(maxlen=CANDLES_N) for tf in TF_DEFS})
fvg_store: Dict[str, List[FVGap]] = defaultdict(list)  # pair -> list of FVGap
sr_store: Dict[str, List[SRZone]] = defaultdict(list)
last_signal_ts: Dict[str, float] = defaultdict(lambda: 0.0)

# ---------------- Utilities ----------------
def candles_to_df(candles: Deque[Candle]) -> pd.DataFrame:
    if len(candles) == 0:
        return pd.DataFrame()
    arr = [{
        "ts": c.ts, "open": c.open, "high": c.high, "low": c.low, "close": c.close, "volume": c.volume
    } for c in candles]
    df = pd.DataFrame(arr).set_index(pd.to_datetime([c["ts"] for c in arr], unit="s"))
    return df

async def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    txt = await resp.text()
                    logger.warning("Telegram send failed %s %s", resp.status, txt)
    except Exception as e:
        logger.exception("Telegram error: %s", e)

# ---------------- Indicators & structural detection ----------------
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df) < max(EMA_LEN, ATR_LEN, 14):
        return df
    df = df.copy()
    df["rsi14"] = ta.rsi(df["close"], length=14)
    st = ta.stoch(high=df["high"], low=df["low"], close=df["close"], k=14, d=3)
    if isinstance(st, pd.DataFrame):
        kcol, dcol = list(st.columns)[:2]
        df["stoch_k"] = st[kcol]
        df["stoch_d"] = st[dcol]
    df["ema20"] = ta.ema(df["close"], length=EMA_LEN)
    df["atr10"] = ta.atr(df["high"], df["low"], df["close"], length=ATR_LEN)
    df["keltner_upper"] = df["ema20"] + KC_MULT * df["atr10"]
    df["keltner_lower"] = df["ema20"] - KC_MULT * df["atr10"]
    return df

def detect_fvg_for_df(pair: str, tf: str, df: pd.DataFrame) -> List[FVGap]:
    # Detect newly created FVGs based on pattern low[i] > high[i-2] (bull) or high[i] < low[i-2] (bear)
    gaps: List[FVGap] = []
    if df.shape[0] < 3:
        return gaps
    last_idx = df.index[-1]
    # find indices where gap exists (iterate last few bars)
    for i in range(2, min(len(df), 50)):
        row = df.iloc[-i]
        row_m2 = df.iloc[-i-2]
        # bullish gap: low[i] > high[i-2]
        if row["low"] > row_m2["high"]:
            top = float(row_m2["high"])
            bottom = float(row["low"])
            gaps.append(FVGap(pair=pair, tf=tf, side="bull", top=top, bottom=bottom))
        elif row["high"] < row_m2["low"]:
            top = float(row["high"])
            bottom = float(row_m2["low"])
            gaps.append(FVGap(pair=pair, tf=tf, side="bear", top=top, bottom=bottom))
    return gaps

def update_fvg_store(pair: str, tf: str, df: pd.DataFrame):
    new = detect_fvg_for_df(pair, tf, df)
    existing = fvg_store[pair]
    # naive dedupe: by top/bottom within tiny epsilon
    eps = 1e-6
    for g in new:
        if not any(abs(g.top - e.top) < eps and abs(g.bottom - e.bottom) < eps for e in existing):
            existing.append(g)
            logger.info("New FVG %s %s %s->%s", pair, tf, g.side, (g.top, g.bottom))

def expire_and_fill_fvgs(pair: str, current_price: float):
    # mark gaps filled if price enters zone
    for g in fvg_store[pair]:
        if g.filled:
            continue
        if g.side == "bull":
            if current_price <= g.top:  # price moved back into/through the gap
                g.filled = True
                logger.info("FVG filled (bull) %s %s", pair, (g.top, g.bottom))
        else:
            if current_price >= g.bottom:
                g.filled = True
                logger.info("FVG filled (bear) %s %s", pair, (g.top, g.bottom))

# Simple swing SR detection & clustering
def detect_swing_points(df: pd.DataFrame, lookback=3) -> Tuple[List[Tuple[int,float]], List[Tuple[int,float]]]:
    highs = []
    lows = []
    if len(df) < (2*lookback + 1):
        return highs, lows
    
    for i in range(lookback, len(df)-lookback):
        hi = df["high"].iloc[i]
        lo = df["low"].iloc[i]
        if hi == df["high"].iloc[i-lookback:i+lookback+1].max():
            highs.append((i, float(hi)))
        if lo == df["low"].iloc[i-lookback:i+lookback+1].min():
            lows.append((i, float(lo)))
    return highs, lows

def cluster_sr_zones(pair: str, df: pd.DataFrame, tol=0.003):
    highs, lows = detect_swing_points(df, lookback=3)
    zones = sr_store[pair]
    
    # cluster highs as resistance
    for _, price in highs:
        matched = False
        for z in zones:
            # if price close to zone's high/low
            mid = (z.low + z.high) / 2.0
            if abs(price - mid) / mid <= tol:
                z.strength += 1
                z.last_touched = time.time()
                matched = True
                break
        if not matched:
            # create small zone around that price
            padding = price * 0.0015
            zones.append(SRZone(pair=pair, low=price - padding, high=price + padding, strength=1))
    
    # same for lows
    for _, price in lows:
        matched = False
        for z in zones:
            mid = (z.low + z.high) / 2.0
            if abs(price - mid) / mid <= tol:
                z.strength += 1
                z.last_touched = time.time()
                matched = True
                break
        if not matched:
            padding = price * 0.0015
            zones.append(SRZone(pair=pair, low=price - padding, high=price + padding, strength=1))
    
    # prune old weak zones
    sr_store[pair] = [z for z in zones if (time.time() - z.last_touched) < 60*60*24 or z.strength > 1]

# ---------------- Breakout detection ----------------
def is_breakout(df: pd.DataFrame, direction: str, range_bars=HTF_RANGE_BARS) -> bool:
    if df.empty or len(df) < range_bars + 1:
        return False
    
    recent = df.iloc[-(range_bars+1):-1]  # last N bars excluding current
    high = recent["high"].max()
    low = recent["low"].min()
    last = df.iloc[-1]
    
    body = abs(last["close"] - last["open"])
    rng = last["high"] - last["low"]
    if rng <= 0:
        return False
    
    body_ratio = body / rng
    
    if direction == "up":
        cond = last["close"] > high and body_ratio >= BREAKOUT_BODY_RATIO
        return bool(cond)
    else:
        cond = last["close"] < low and body_ratio >= BREAKOUT_BODY_RATIO
        return bool(cond)

# ---------------- Decision & scoring ----------------
def compute_score(pair: str, df_htf: pd.DataFrame, df_mtf: pd.DataFrame, df_ltf: pd.DataFrame) -> Tuple[str, List[str], int]:
    """
    Returns (side, reasons, score) where side in {'buy','sell','none'}.
    """
    side = "none"
    reasons: List[str] = []
    score = 0
    
    # safety checks
    if df_mtf.empty or df_htf.empty:
        return side, reasons, score
    
    # last values
    m_last = df_mtf.iloc[-1]
    h_last = df_htf.iloc[-1]
    l_last = df_ltf.iloc[-1] if not df_ltf.empty else m_last
    
    # basic indicator confirmations on MTF
    rsi = float(m_last.get("rsi14", np.nan))
    st_k = float(m_last.get("stoch_k", np.nan)) if "stoch_k" in m_last else np.nan
    k_upper = float(m_last.get("keltner_upper", np.nan)) if "keltner_upper" in m_last else np.nan
    k_lower = float(m_last.get("keltner_lower", np.nan)) if "keltner_lower" in m_last else np.nan
    
    # HTF breakout raw
    breakout_up = is_breakout(df_htf, "up")
    breakout_down = is_breakout(df_htf, "down")
    
    if breakout_up:
        score += 25
        reasons.append("HTF breakout up")
    if breakout_down:
        score += 25
        reasons.append("HTF breakout down")
    
    # FVG alignment
    # bullish FVG that price is inside
    for g in fvg_store[pair]:
        if g.filled:
            continue
        if g.tf != MTF:  # prioritize MTF gaps
            continue
        if g.side == "bull" and l_last["close"] <= g.top and l_last["close"] >= g.bottom:
            score += 30
            reasons.append("Inside bullish FVG")
        if g.side == "bear" and l_last["close"] >= g.bottom and l_last["close"] <= g.top:
            score += 30
            reasons.append("Inside bearish FVG")
    
    # RSI / stochastic confirmation
    if not math.isnan(rsi):
        if rsi < 30:
            score += 20
            reasons.append(f"RSI {rsi:.1f} <30")
        elif rsi > 70:
            score += 20
            reasons.append(f"RSI {rsi:.1f} >70")
    
    if not math.isnan(st_k):
        if st_k < 20:
            score += 10
            reasons.append(f"StochK {st_k:.1f} <20")
        elif st_k > 80:
            score += 10
            reasons.append(f"StochK {st_k:.1f} >80")
    
    # Keltner: price outside channel
    if not math.isnan(k_lower) and not math.isnan(k_upper):
        if m_last["close"] < k_lower:
            score += 10
            reasons.append("Close below Keltner lower")
        elif m_last["close"] > k_upper:
            score += 10
            reasons.append("Close above Keltner upper")
    
    # HTF momentum conflict penalty: e.g., HTF RSI opposes
    h_rsi = float(h_last.get("rsi14", np.nan))
    if not math.isnan(h_rsi) and not math.isnan(rsi):
        # if HTF RSI on opposite extreme reduce score
        if (rsi < 40 and h_rsi > 60) or (rsi > 60 and h_rsi < 40):
            score -= 40
            reasons.append(f"HTF momentum opposes (HTF RSI {h_rsi:.1f})")
    
    # Decide side heuristically
    if score >= 60:
        # decide direction: prefer breakout direction or indicator direction
        if breakout_up or (rsi < 40 and m_last["close"] > h_last["close"]):  # some heuristic
            side = "buy"
        elif breakout_down or (rsi > 60 and m_last["close"] < h_last["close"]):
            side = "sell"
        else:
            # fallback: base on MTF close vs HTF ema
            if m_last["close"] > h_last.get("ema20", m_last["close"]):
                side = "buy"
            else:
                side = "sell"
    else:
        side = "none"
    
    return side, reasons, score

# ---------------- Worker per pair ----------------
async def pair_worker(pair: str):
    """
    Maintains buffers, computes indicators, updates structural data, and issues signals.
    get_live_candle(pair) must be implemented to stream real-time candles.
    """
    logger.info("Starting worker for %s", pair)
    
    # initialize test / historical load (optional) - here we rely on get_live_candle generating history
    while True:
        try:
            # fetch latest candle(s) from feed (stub below)
            new_candles = await get_live_candles_stub(pair)
            
            # push into buffers (each candle has timeframe attribute in this stub; in real feed you'll produce candles per tf)
            for tf, candle in new_candles:
                buffers[pair][tf].append(candle)
            
            # For each tf update indicators & structures
            for tf, dq in buffers[pair].items():
                df = candles_to_df(dq)
                if not df.empty:
                    df = add_indicators(df)
                    
                    # detect FVGs on MTF
                    if tf == MTF:
                        update_fvg_store(pair, tf, df)
                    
                    # detect SR zones (every so often)
                    if len(df) >= 50:
                        cluster_sr_zones(pair, df)
            
            # expire FVGs using latest price
            latest_price = None
            # pick most recent candle from MTF or LTF
            if buffers[pair][MTF]:
                latest_price = buffers[pair][MTF][-1].close
            elif buffers[pair][LTF]:
                latest_price = buffers[pair][LTF][-1].close
            
            if latest_price:
                expire_and_fill_fvgs(pair, latest_price)
            
            # compute signal using HTF, MTF, LTF dfs
            df_htf = add_indicators(candles_to_df(buffers[pair][HTF]))
            df_mtf = add_indicators(candles_to_df(buffers[pair][MTF]))
            df_ltf = add_indicators(candles_to_df(buffers[pair][LTF]))
            
            side, reasons, score = compute_score(pair, df_htf, df_mtf, df_ltf)
            
            now = time.time()
            if side != "none" and (now - last_signal_ts[pair]) > SIGNAL_DEBOUNCE:
                # Build friendly message
                txt = f"🔔 <b>{pair}</b> SIGNAL: <b>{side.upper()}</b>\nScore: {score}\n"
                for r in reasons:
                    txt += f"- {r}\n"
                if not df_mtf.empty:
                    txt += f"Price: {df_mtf.iloc[-1]['close']:.5f} Time(UTC): {df_mtf.index[-1].strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                await send_telegram(txt)
                last_signal_ts[pair] = now
                logger.info("Sent signal %s %s (score=%d)", pair, side, score)
            
            await asyncio.sleep(POLL_INTERVAL)
            
        except Exception as e:
            logger.exception("Error in pair_worker %s: %s", pair, e)
            await asyncio.sleep(1.0)

# ------------------ TEST / STUB live feed ------------------
async def get_live_candles_stub(pair: str):
    """
    TEST STUB: Returns a list of (tf, Candle) tuples — simulate 30s, 1m, 3m, 5m candles by aggregating a synthetic price.
    Replace this with Pocket Option websocket subscription code that yields completed candles per timeframe.
    """
    # For testing, produce a new 30s tick and aggregate into higher TFs
    now = time.time()
    base = 1.1000 + 0.001 * math.sin(now / 37.0 + hash(pair) % 10)  # small random walk
    jitter = (np.random.randn() * 0.0002)
    price = base + jitter
    
    candles_out = []
    
    # Create 30s candle
    c30 = Candle(ts=now, open=price - 0.0001, high=price + 0.0002, low=price - 0.0002, close=price, volume=100)
    candles_out.append(("30s", c30))
    
    # aggregate to 1m: take last two 30s from buffer if available
    # naive approach: if previous exists in buffer, create 1m new candle occasionally
    # We'll create 1m candles every 2*POLL_INTERVAL seconds
    if int(now) % 60 < 2:
        c1 = Candle(ts=now, open=price - 0.0003, high=price + 0.0004, low=price - 0.0004, close=price, volume=240)
        candles_out.append(("1m", c1))
    
    if int(now) % 180 < 3:
        c3 = Candle(ts=now, open=price - 0.0005, high=price + 0.0008, low=price - 0.0007, close=price, volume=600)
        candles_out.append(("3m", c3))
    
    if int(now) % 300 < 3:
        c5 = Candle(ts=now, open=price - 0.0009, high=price + 0.0012, low=price - 0.0011, close=price, volume=1200)
        candles_out.append(("5m", c5))
    
    return candles_out

# ---------------- Main ----------------
async def main():
    # start worker tasks for each pair
    tasks = []
    for p in PAIRS:
        t = asyncio.create_task(pair_worker(p))
        tasks.append(t)
        await asyncio.sleep(0.2)
    
    logger.info("Workers started for pairs: %s", PAIRS)
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
