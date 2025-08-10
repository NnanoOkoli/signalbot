import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.daily_stats = {
            'total_trades': 0,
            'total_loss': 0.0,
            'total_profit': 0.0,
            'last_reset': datetime.now().date()
        }
        
    def calculate_position_size(self, signal: Dict[str, Any], account_balance: float, 
                              risk_per_trade: float = None) -> Dict[str, Any]:
        """Calculate optimal position size based on risk management rules"""
        try:
            # Reset daily stats if it's a new day
            self._reset_daily_stats_if_needed()
            
            # Check daily limits
            if not self._check_daily_limits():
                return {
                    'position_size': 0,
                    'reason': 'Daily limits exceeded',
                    'risk_level': 'high'
                }
            
            # Calculate base position size
            base_size = self._calculate_base_position_size(signal, account_balance, risk_per_trade)
            
            # Apply risk adjustments
            adjusted_size = self._apply_risk_adjustments(base_size, signal, account_balance)
            
            # Validate final position size
            final_size = self._validate_position_size(adjusted_size, account_balance)
            
            return {
                'position_size': final_size,
                'risk_percentage': (final_size / account_balance) * 100 if account_balance > 0 else 0,
                'risk_level': signal.get('risk_level', 'medium'),
                'confidence': signal.get('confidence', 0.5),
                'stop_loss': self._calculate_stop_loss(signal, final_size),
                'take_profit': self._calculate_take_profit(signal, final_size)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return {
                'position_size': 0,
                'reason': f'Error: {str(e)}',
                'risk_level': 'high'
            }
    
    def _reset_daily_stats_if_needed(self):
        """Reset daily statistics if it's a new day"""
        current_date = datetime.now().date()
        if current_date != self.daily_stats['last_reset']:
            self.daily_stats = {
                'total_trades': 0,
                'total_loss': 0.0,
                'total_profit': 0.0,
                'last_reset': current_date
            }
    
    def _check_daily_limits(self) -> bool:
        """Check if daily trading limits are exceeded"""
        # Check daily trade count
        if self.daily_stats['total_trades'] >= self.config.MAX_DAILY_TRADES:
            return False
        
        # Check daily loss limit
        if self.daily_stats['total_loss'] >= self.config.MAX_DAILY_LOSS:
            return False
        
        return True
    
    def _calculate_base_position_size(self, signal: Dict[str, Any], account_balance: float, 
                                    risk_per_trade: float = None) -> float:
        """Calculate base position size based on Kelly Criterion and signal confidence"""
        if risk_per_trade is None:
            risk_per_trade = self.config.DEFAULT_INVESTMENT
        
        # Get signal confidence
        confidence = signal.get('confidence', 0.5)
        
        # Kelly Criterion calculation
        win_rate = confidence
        avg_win = 0.8  # Typical binary option payout
        avg_loss = 1.0  # Full loss on binary option
        
        if avg_loss > 0:
            kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        else:
            kelly_fraction = 0.1  # Default to 10%
        
        # Calculate position size
        position_size = account_balance * kelly_fraction
        
        # Apply confidence multiplier
        confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5 to 1.0
        position_size *= confidence_multiplier
        
        return position_size
    
    def _apply_risk_adjustments(self, base_size: float, signal: Dict[str, Any], 
                               account_balance: float) -> float:
        """Apply risk-based adjustments to position size"""
        adjusted_size = base_size
        
        # Risk level adjustments
        risk_level = signal.get('risk_level', 'medium')
        if risk_level == 'high':
            adjusted_size *= 0.5  # Reduce size for high-risk signals
        elif risk_level == 'low':
            adjusted_size *= 1.2  # Increase size for low-risk signals
        
        # Trend strength adjustment
        market_conditions = signal.get('analysis', {}).get('market_conditions', {})
        trend_strength = market_conditions.get('trend', {}).get('strength', 0.5)
        
        if trend_strength > 0.8:
            adjusted_size *= 1.1  # Strong trend
        elif trend_strength < 0.4:
            adjusted_size *= 0.7  # Weak trend
        
        # Volatility adjustment
        volatility = market_conditions.get('volatility', {}).get('bb_width', 0.05)
        if volatility > 0.08:  # High volatility
            adjusted_size *= 0.8
        elif volatility < 0.03:  # Low volatility
            adjusted_size *= 1.1
        
        # Ensure position size is within limits
        max_size = min(self.config.MAX_INVESTMENT, account_balance * 0.1)
        min_size = self.config.MIN_INVESTMENT
        
        adjusted_size = max(min_size, min(adjusted_size, max_size))
        
        return adjusted_size
    
    def _validate_position_size(self, position_size: float, account_balance: float) -> float:
        """Validate and adjust position size if necessary"""
        # Ensure minimum investment
        if position_size < self.config.MIN_INVESTMENT:
            position_size = self.config.MIN_INVESTMENT
        
        # Ensure maximum investment
        if position_size > self.config.MAX_INVESTMENT:
            position_size = self.config.MAX_INVESTMENT
        
        # Ensure position size doesn't exceed account balance
        if position_size > account_balance:
            position_size = account_balance * 0.95  # Leave 5% buffer
        
        # Ensure position size doesn't exceed maximum risk per trade
        max_risk_amount = account_balance * (self.config.STOP_LOSS_PERCENTAGE / 100)
        if position_size > max_risk_amount:
            position_size = max_risk_amount
        
        return position_size
    
    def _calculate_stop_loss(self, signal: Dict[str, Any], position_size: float) -> Dict[str, Any]:
        """Calculate stop loss levels"""
        market_conditions = signal.get('analysis', {}).get('market_conditions', {})
        support_resistance = market_conditions.get('support_resistance', {})
        
        # Calculate stop loss based on support/resistance levels
        if signal.get('direction') == 'call':
            # For call options, stop loss below support
            stop_loss_level = support_resistance.get('support_1', 0)
            stop_loss_distance = 0.02  # 2% below entry
        else:
            # For put options, stop loss above resistance
            stop_loss_level = support_resistance.get('resistance_1', 0)
            stop_loss_distance = 0.02  # 2% above entry
        
        # Calculate stop loss amount
        stop_loss_amount = position_size * (self.config.STOP_LOSS_PERCENTAGE / 100)
        
        return {
            'level': stop_loss_level,
            'distance': stop_loss_distance,
            'amount': stop_loss_amount,
            'percentage': self.config.STOP_LOSS_PERCENTAGE
        }
    
    def _calculate_take_profit(self, signal: Dict[str, Any], position_size: float) -> Dict[str, Any]:
        """Calculate take profit levels"""
        # Risk-reward ratio (typically 1:1.5 for binary options)
        risk_reward_ratio = 1.5
        
        # Calculate take profit based on stop loss
        stop_loss_percentage = self.config.STOP_LOSS_PERCENTAGE / 100
        take_profit_percentage = stop_loss_percentage * risk_reward_ratio
        
        take_profit_amount = position_size * take_profit_percentage
        
        return {
            'percentage': take_profit_percentage * 100,
            'amount': take_profit_amount,
            'risk_reward_ratio': risk_reward_ratio
        }
    
    def update_trade_result(self, trade_result: Dict[str, Any]):
        """Update daily statistics with trade result"""
        self.daily_stats['total_trades'] += 1
        
        if trade_result.get('profit_loss', 0) > 0:
            self.daily_stats['total_profit'] += trade_result['profit_loss']
        else:
            self.daily_stats['total_loss'] += abs(trade_result['profit_loss'])
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics"""
        return {
            'daily_trades': self.daily_stats['total_trades'],
            'daily_loss': self.daily_stats['total_loss'],
            'daily_profit': self.daily_stats['total_profit'],
            'daily_net': self.daily_stats['total_profit'] - self.daily_stats['total_loss'],
            'max_daily_trades': self.config.MAX_DAILY_TRADES,
            'max_daily_loss': self.config.MAX_DAILY_LOSS,
            'remaining_trades': max(0, self.config.MAX_DAILY_TRADES - self.daily_stats['total_trades']),
            'remaining_loss_limit': max(0, self.config.MAX_DAILY_LOSS - self.daily_stats['total_loss'])
        }
    
    def calculate_portfolio_risk(self, open_positions: list, account_balance: float) -> Dict[str, Any]:
        """Calculate overall portfolio risk"""
        if not open_positions:
            return {
                'total_risk': 0,
                'risk_percentage': 0,
                'max_drawdown': 0,
                'correlation_risk': 'low'
            }
        
        total_exposure = sum(pos.get('position_size', 0) for pos in open_positions)
        total_risk = sum(pos.get('risk_amount', 0) for pos in open_positions)
        
        # Calculate correlation risk
        assets = [pos.get('asset', '') for pos in open_positions]
        correlation_risk = 'high' if len(set(assets)) < len(assets) * 0.7 else 'medium'
        
        # Calculate potential max drawdown
        max_drawdown = (total_risk / account_balance) * 100 if account_balance > 0 else 0
        
        return {
            'total_exposure': total_exposure,
            'total_risk': total_risk,
            'risk_percentage': (total_risk / account_balance) * 100 if account_balance > 0 else 0,
            'max_drawdown': max_drawdown,
            'correlation_risk': correlation_risk,
            'position_count': len(open_positions)
        }
    
    def should_close_position(self, position: Dict[str, Any], current_price: float) -> bool:
        """Determine if a position should be closed based on risk management rules"""
        # Check stop loss
        stop_loss = position.get('stop_loss', {})
        if stop_loss.get('level', 0) > 0:
            if position.get('direction') == 'call' and current_price <= stop_loss['level']:
                return True
            elif position.get('direction') == 'put' and current_price >= stop_loss['level']:
                return True
        
        # Check take profit
        take_profit = position.get('take_profit', {})
        if take_profit.get('percentage', 0) > 0:
            entry_price = position.get('entry_price', 0)
            if entry_price > 0:
                if position.get('direction') == 'call' and current_price >= entry_price * (1 + take_profit['percentage'] / 100):
                    return True
                elif position.get('direction') == 'put' and current_price <= entry_price * (1 - take_profit['percentage'] / 100):
                    return True
        
        return False
