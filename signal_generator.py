import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import logging
from technical_indicators import TechnicalIndicators

class SignalGenerator:
    def __init__(self, config, technical_indicators: TechnicalIndicators):
        self.config = config
        self.indicators = technical_indicators
        self.logger = logging.getLogger(__name__)
        
    def generate_signal(self, asset: str, ohlcv_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate trading signal for a given asset"""
        try:
            if len(ohlcv_data) < 100:
                return self._create_neutral_signal(asset, "Insufficient data")
            
            # Calculate all technical indicators
            indicators = self.indicators.get_all_indicators(ohlcv_data)
            if not indicators:
                return self._create_neutral_signal(asset, "Failed to calculate indicators")
            
            # Analyze market conditions
            market_analysis = self._analyze_market_conditions(ohlcv_data, indicators)
            
            # Generate signal based on analysis
            signal = self._analyze_indicators(ohlcv_data, indicators, market_analysis)
            
            # Apply OTC-specific filters
            signal = self._apply_otc_filters(signal, indicators, market_analysis)
            
            # Calculate confidence score
            signal['confidence'] = self._calculate_confidence(signal, indicators, market_analysis)
            
            # Add metadata
            signal['timestamp'] = datetime.now().isoformat()
            signal['asset'] = asset
            signal['analysis_period'] = len(ohlcv_data)
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error generating signal for {asset}: {str(e)}")
            return self._create_neutral_signal(asset, f"Error: {str(e)}")
    
    def _analyze_market_conditions(self, ohlcv_data: pd.DataFrame, indicators: Dict) -> Dict[str, Any]:
        """Analyze overall market conditions"""
        close = ohlcv_data['close']
        high = ohlcv_data['high']
        low = ohlcv_data['low']
        
        # Trend analysis
        current_price = close.iloc[-1]
        ema_20 = indicators['ema_20'].iloc[-1]
        ema_50 = indicators['ema_50'].iloc[-1]
        sma_20 = indicators['sma_20'].iloc[-1]
        sma_50 = indicators['sma_50'].iloc[-1]
        
        # Volatility analysis
        atr = indicators['atr'].iloc[-1]
        bb_upper = indicators['bb_upper'].iloc[-1]
        bb_lower = indicators['bb_lower'].iloc[-1]
        bb_middle = indicators['bb_middle'].iloc[-1]
        
        # Volume analysis
        obv = indicators.get('obv', pd.Series([0]))
        obv_trend = obv.iloc[-1] - obv.iloc[-5] if len(obv) >= 5 else 0
        
        return {
            'trend': {
                'direction': 'bullish' if current_price > ema_20 > ema_50 else 'bearish' if current_price < ema_20 < ema_50 else 'sideways',
                'strength': indicators['trend_strength'],
                'ema_alignment': current_price > ema_20 > ema_50,
                'sma_alignment': current_price > sma_20 > sma_50
            },
            'volatility': {
                'atr': atr,
                'bb_width': (bb_upper - bb_lower) / bb_middle,
                'price_position': (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
            },
            'volume': {
                'obv_trend': obv_trend,
                'volume_confirmation': obv_trend > 0
            },
            'support_resistance': indicators['support_resistance']
        }
    
    def _analyze_indicators(self, ohlcv_data: pd.DataFrame, indicators: Dict, market_analysis: Dict) -> Dict[str, Any]:
        """Analyze individual technical indicators"""
        close = ohlcv_data['close']
        current_price = close.iloc[-1]
        
        # RSI Analysis
        rsi = indicators['rsi'].iloc[-1]
        rsi_signal = self._analyze_rsi(rsi)
        
        # MACD Analysis
        macd_signal = self._analyze_macd(indicators)
        
        # Bollinger Bands Analysis
        bb_signal = self._analyze_bollinger_bands(indicators, current_price)
        
        # Stochastic Analysis
        stoch_signal = self._analyze_stochastic(indicators)
        
        # ADX Analysis (Trend Strength)
        adx = indicators['adx'].iloc[-1]
        adx_signal = 'strong_trend' if adx > 25 else 'weak_trend'
        
        # Williams %R Analysis
        williams_r = indicators['williams_r'].iloc[-1]
        williams_signal = self._analyze_williams_r(williams_r)
        
        # CCI Analysis
        cci = indicators['cci'].iloc[-1]
        cci_signal = self._analyze_cci(cci)
        
        # Momentum Analysis
        momentum = indicators['momentum'].iloc[-1]
        momentum_signal = 'positive' if momentum > 0 else 'negative'
        
        return {
            'rsi': rsi_signal,
            'macd': macd_signal,
            'bollinger_bands': bb_signal,
            'stochastic': stoch_signal,
            'adx': adx_signal,
            'williams_r': williams_signal,
            'cci': cci_signal,
            'momentum': momentum_signal,
            'market_conditions': market_analysis
        }
    
    def _analyze_rsi(self, rsi: float) -> str:
        """Analyze RSI indicator"""
        if pd.isna(rsi):
            return 'neutral'
        
        if rsi < 30:
            return 'oversold'
        elif rsi > 70:
            return 'overbought'
        elif rsi < 40:
            return 'approaching_oversold'
        elif rsi > 60:
            return 'approaching_overbought'
        else:
            return 'neutral'
    
    def _analyze_macd(self, indicators: Dict) -> str:
        """Analyze MACD indicator"""
        macd = indicators['macd'].iloc[-1]
        macd_signal = indicators['macd_signal'].iloc[-1]
        macd_hist = indicators['macd_histogram'].iloc[-1]
        
        if pd.isna(macd) or pd.isna(macd_signal):
            return 'neutral'
        
        # MACD crossover signals
        if macd > macd_signal and macd_hist > 0:
            return 'bullish_crossover'
        elif macd < macd_signal and macd_hist < 0:
            return 'bearish_crossover'
        elif macd > macd_signal:
            return 'bullish'
        elif macd < macd_signal:
            return 'bearish'
        else:
            return 'neutral'
    
    def _analyze_bollinger_bands(self, indicators: Dict, current_price: float) -> str:
        """Analyze Bollinger Bands"""
        bb_upper = indicators['bb_upper'].iloc[-1]
        bb_lower = indicators['bb_lower'].iloc[-1]
        bb_middle = indicators['bb_middle'].iloc[-1]
        
        if pd.isna(bb_upper) or pd.isna(bb_lower):
            return 'neutral'
        
        if current_price <= bb_lower:
            return 'oversold'
        elif current_price >= bb_upper:
            return 'overbought'
        elif current_price < bb_middle:
            return 'below_middle'
        else:
            return 'above_middle'
    
    def _analyze_stochastic(self, indicators: Dict) -> str:
        """Analyze Stochastic Oscillator"""
        stoch_k = indicators['stoch_k'].iloc[-1]
        stoch_d = indicators['stoch_d'].iloc[-1]
        
        if pd.isna(stoch_k) or pd.isna(stoch_d):
            return 'neutral'
        
        if stoch_k < 20 and stoch_d < 20:
            return 'oversold'
        elif stoch_k > 80 and stoch_d > 80:
            return 'overbought'
        elif stoch_k > stoch_d:
            return 'bullish_crossover'
        elif stoch_k < stoch_d:
            return 'bearish_crossover'
        else:
            return 'neutral'
    
    def _analyze_williams_r(self, williams_r: float) -> str:
        """Analyze Williams %R"""
        if pd.isna(williams_r):
            return 'neutral'
        
        if williams_r < -80:
            return 'oversold'
        elif williams_r > -20:
            return 'overbought'
        elif williams_r < -60:
            return 'approaching_oversold'
        elif williams_r > -40:
            return 'approaching_overbought'
        else:
            return 'neutral'
    
    def _analyze_cci(self, cci: float) -> str:
        """Analyze Commodity Channel Index"""
        if pd.isna(cci):
            return 'neutral'
        
        if cci > 100:
            return 'overbought'
        elif cci < -100:
            return 'oversold'
        elif cci > 0:
            return 'positive'
        else:
            return 'negative'
    
    def _apply_otc_filters(self, signal: Dict, indicators: Dict, market_analysis: Dict) -> Dict:
        """Apply OTC-specific filters and adjustments"""
        # OTC markets are more volatile, so we need stricter filters
        
        # Check if trend is strong enough
        trend_strength = market_analysis['trend']['strength']
        if trend_strength < self.config.TREND_STRENGTH_THRESHOLD:
            signal['otc_filter'] = 'weak_trend'
            return signal
        
        # Check volatility conditions
        volatility = market_analysis['volatility']
        if volatility['bb_width'] > 0.1:  # High volatility
            signal['otc_filter'] = 'high_volatility'
            return signal
        
        # Check for clear directional bias
        bullish_signals = 0
        bearish_signals = 0
        
        for indicator, value in signal.items():
            if indicator in ['rsi', 'macd', 'bollinger_bands', 'stochastic', 'williams_r', 'cci']:
                if 'bullish' in str(value) or 'oversold' in str(value):
                    bullish_signals += 1
                elif 'bearish' in str(value) or 'overbought' in str(value):
                    bearish_signals += 1
        
        # Require clear majority for OTC signals
        total_signals = bullish_signals + bearish_signals
        if total_signals > 0:
            if bullish_signals / total_signals > 0.6:
                signal['otc_filter'] = 'strong_bullish_bias'
            elif bearish_signals / total_signals > 0.6:
                signal['otc_filter'] = 'strong_bearish_bias'
            else:
                signal['otc_filter'] = 'mixed_signals'
        
        return signal
    
    def _calculate_confidence(self, signal: Dict, indicators: Dict, market_analysis: Dict) -> float:
        """Calculate overall signal confidence score"""
        confidence = 0.5  # Base confidence
        
        # Trend strength contribution
        trend_strength = market_analysis['trend']['strength']
        confidence += trend_strength * 0.2
        
        # Indicator agreement
        bullish_count = 0
        bearish_count = 0
        
        for indicator, value in signal.items():
            if indicator in ['rsi', 'macd', 'bollinger_bands', 'stochastic', 'williams_r', 'cci']:
                if 'bullish' in str(value) or 'oversold' in str(value):
                    bullish_count += 1
                elif 'bearish' in str(value) or 'overbought' in str(value):
                    bearish_count += 1
        
        # Calculate agreement ratio
        total_indicators = bullish_count + bearish_count
        if total_indicators > 0:
            agreement_ratio = max(bullish_count, bearish_count) / total_indicators
            confidence += agreement_ratio * 0.3
        
        # Volume confirmation
        if market_analysis['volume']['volume_confirmation']:
            confidence += 0.1
        
        # ADX strength
        adx = indicators['adx'].iloc[-1]
        if not pd.isna(adx):
            if adx > 25:
                confidence += 0.1
            elif adx < 15:
                confidence -= 0.1
        
        # OTC filter adjustment
        otc_filter = signal.get('otc_filter', '')
        if 'strong' in otc_filter:
            confidence += 0.1
        elif 'weak' in otc_filter or 'mixed' in otc_filter:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _create_neutral_signal(self, asset: str, reason: str) -> Dict[str, Any]:
        """Create a neutral signal when analysis fails"""
        return {
            'asset': asset,
            'signal': 'NEUTRAL',
            'direction': 'none',
            'confidence': 0.5,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'recommendation': 'wait',
            'risk_level': 'low'
        }
    
    def generate_final_signal(self, analysis: Dict) -> Dict[str, Any]:
        """Generate final trading signal based on analysis"""
        confidence = analysis.get('confidence', 0.5)
        
        # Determine signal direction
        bullish_signals = 0
        bearish_signals = 0
        
        for indicator, value in analysis.items():
            if indicator in ['rsi', 'macd', 'bollinger_bands', 'stochastic', 'williams_r', 'cci']:
                if 'bullish' in str(value) or 'oversold' in str(value):
                    bullish_signals += 1
                elif 'bearish' in str(value) or 'overbought' in str(value):
                    bearish_signals += 1
        
        # Determine signal type
        if confidence >= self.config.SIGNAL_CONFIDENCE_THRESHOLD:
            if bullish_signals > bearish_signals:
                signal_type = 'BUY'
                direction = 'call'
            elif bearish_signals > bullish_signals:
                signal_type = 'SELL'
                direction = 'put'
            else:
                signal_type = 'NEUTRAL'
                direction = 'none'
        else:
            signal_type = 'NEUTRAL'
            direction = 'none'
        
        # Determine risk level
        if confidence >= 0.8:
            risk_level = 'low'
        elif confidence >= 0.6:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        # Generate recommendation
        if signal_type == 'NEUTRAL':
            recommendation = 'wait'
        elif confidence >= 0.8:
            recommendation = 'strong'
        elif confidence >= 0.6:
            recommendation = 'moderate'
        else:
            recommendation = 'weak'
        
        return {
            'signal_type': signal_type,
            'direction': direction,
            'confidence': confidence,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'analysis': analysis
        }
