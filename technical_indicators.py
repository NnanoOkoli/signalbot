import numpy as np
import pandas as pd
import ta
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class TechnicalIndicators:
    def __init__(self, config):
        self.config = config
        
    def calculate_rsi(self, prices: pd.Series, period: int = None) -> pd.Series:
        """Calculate Relative Strength Index"""
        period = period or self.config.RSI_PERIOD
        return ta.momentum.RSIIndicator(prices, window=period).rsi()
    
    def calculate_macd(self, prices: pd.Series, fast: int = None, slow: int = None, signal: int = None) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD, Signal, and Histogram"""
        fast = fast or self.config.MACD_FAST
        slow = slow or self.config.MACD_SLOW
        signal_period = signal or self.config.MACD_SIGNAL
        
        macd = ta.trend.MACD(prices, window_fast=fast, window_slow=slow, window_sign=signal_period)
        return macd.macd(), macd.macd_signal(), macd.macd_diff()
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = None, std: float = None) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        period = period or self.config.BOLLINGER_PERIOD
        std = std or self.config.BOLLINGER_STD
        
        bb = ta.volatility.BollingerBands(prices, window=period, window_dev=std)
        return bb.bollinger_hband(), bb.bollinger_mavg(), bb.bollinger_lband()
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        stoch = ta.momentum.StochasticOscillator(high, low, close, window=period)
        return stoch.stoch(), stoch.stoch_signal()
    
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        return ta.trend.ADXIndicator(high, low, close, window=period).adx()
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        return ta.volatility.AverageTrueRange(high, low, close, window=period).average_true_range()
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return ta.trend.EMAIndicator(prices, window=period).ema_indicator()
    
    def calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return ta.trend.SMAIndicator(prices, window=period).sma_indicator()
    
    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        return ta.momentum.WilliamsRIndicator(high, low, close, window=period).williams_r()
    
    def calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index"""
        return ta.trend.CCIIndicator(high, low, close, window=period).cci()
    
    def calculate_momentum(self, prices: pd.Series, period: int = 10) -> pd.Series:
        """Calculate Momentum"""
        return ta.momentum.ROCIndicator(prices, window=period).roc()
    
    def calculate_volume_indicators(self, close: pd.Series, volume: pd.Series) -> Dict[str, pd.Series]:
        """Calculate Volume-based indicators"""
        indicators = {}
        
        # On Balance Volume
        indicators['obv'] = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
        
        # Volume Weighted Average Price
        indicators['vwap'] = ta.volume.VolumeWeightedAveragePrice(close, volume).volume_weighted_average_price()
        
        # Accumulation/Distribution Line
        indicators['adl'] = ta.volume.AccDistIndexIndicator(close, volume).acc_dist_index()
        
        return indicators
    
    def calculate_support_resistance(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> Dict[str, float]:
        """Calculate Support and Resistance levels"""
        recent_high = high.tail(period).max()
        recent_low = low.tail(period).min()
        current_price = close.iloc[-1]
        
        # Calculate pivot points
        pivot = (recent_high + recent_low + current_price) / 3
        r1 = 2 * pivot - recent_low
        s1 = 2 * pivot - recent_high
        r2 = pivot + (recent_high - recent_low)
        s2 = pivot - (recent_high - recent_low)
        
        return {
            'pivot': pivot,
            'resistance_1': r1,
            'resistance_2': r2,
            'support_1': s1,
            'support_2': s2
        }
    
    def calculate_trend_strength(self, prices: pd.Series, period: int = None) -> float:
        """Calculate trend strength using linear regression"""
        period = period or self.config.OTC_ANALYSIS_PERIOD
        
        if len(prices) < period:
            return 0.0
        
        recent_prices = prices.tail(period).values
        x = np.arange(len(recent_prices))
        
        # Linear regression
        slope, intercept = np.polyfit(x, recent_prices, 1)
        
        # Calculate R-squared (trend strength)
        y_pred = slope * x + intercept
        ss_res = np.sum((recent_prices - y_pred) ** 2)
        ss_tot = np.sum((recent_prices - np.mean(recent_prices)) ** 2)
        
        if ss_tot == 0:
            return 0.0
        
        r_squared = 1 - (ss_res / ss_tot)
        trend_strength = abs(slope) * r_squared
        
        return min(trend_strength, 1.0)  # Normalize to 0-1
    
    def calculate_volatility(self, prices: pd.Series, period: int = 20) -> float:
        """Calculate price volatility"""
        if len(prices) < period:
            return 0.0
        
        returns = prices.pct_change().dropna()
        volatility = returns.tail(period).std()
        return float(volatility)
    
    def get_all_indicators(self, ohlcv_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators for a given OHLCV dataset"""
        if len(ohlcv_data) < 50:  # Need minimum data
            return {}
        
        close = ohlcv_data['close']
        high = ohlcv_data['high']
        low = ohlcv_data['low']
        volume = ohlcv_data.get('volume', pd.Series([1] * len(close)))
        
        indicators = {}
        
        # Basic indicators
        indicators['rsi'] = self.calculate_rsi(close)
        indicators['macd'], indicators['macd_signal'], indicators['macd_histogram'] = self.calculate_macd(close)
        indicators['bb_upper'], indicators['bb_middle'], indicators['bb_lower'] = self.calculate_bollinger_bands(close)
        
        # Additional indicators
        indicators['stoch_k'], indicators['stoch_d'] = self.calculate_stochastic(high, low, close)
        indicators['adx'] = self.calculate_adx(high, low, close)
        indicators['atr'] = self.calculate_atr(high, low, close)
        indicators['ema_20'] = self.calculate_ema(close, 20)
        indicators['ema_50'] = self.calculate_ema(close, 50)
        indicators['sma_20'] = self.calculate_sma(close, 20)
        indicators['sma_50'] = self.calculate_sma(close, 50)
        indicators['williams_r'] = self.calculate_williams_r(high, low, close)
        indicators['cci'] = self.calculate_cci(high, low, close)
        indicators['momentum'] = self.calculate_momentum(close)
        
        # Volume indicators
        volume_indicators = self.calculate_volume_indicators(close, volume)
        indicators.update(volume_indicators)
        
        # Support/Resistance
        indicators['support_resistance'] = self.calculate_support_resistance(high, low, close)
        
        # Trend and volatility
        indicators['trend_strength'] = self.calculate_trend_strength(close)
        indicators['volatility'] = self.calculate_volatility(close)
        
        return indicators
