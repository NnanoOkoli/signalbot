import time
import logging
import schedule
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import os

from config import Config
from technical_indicators import TechnicalIndicators
from signal_generator import SignalGenerator
from risk_manager import RiskManager
from pocket_option_api import PocketOptionAPI

class PocketOptionSignalBot:
    def __init__(self):
        self.config = Config()
        self.setup_logging()
        
        # Initialize components
        self.technical_indicators = TechnicalIndicators(self.config)
        self.signal_generator = SignalGenerator(self.config, self.technical_indicators)
        self.risk_manager = RiskManager(self.config)
        self.api = PocketOptionAPI(self.config)
        
        # Bot state
        self.is_running = False
        self.active_signals = {}
        self.trade_history = []
        self.performance_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0
        }
        
        self.logger.info("Pocket Option Signal Bot initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # File handler
        file_handler = logging.FileHandler(self.config.LOG_FILE)
        file_handler.setLevel(getattr(logging, self.config.LOG_LEVEL))
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Root logger
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format=log_format,
            handlers=[file_handler, console_handler]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start the signal bot"""
        try:
            self.logger.info("Starting Pocket Option Signal Bot...")
            
            # Authenticate with Pocket Option
            if not self.api.authenticate():
                self.logger.error("Failed to authenticate with Pocket Option")
                return False
            
            self.is_running = True
            
            # Connect to WebSocket for real-time data
            self.api.connect_websocket()
            
            # Schedule main tasks
            self._schedule_tasks()
            
            # Start the main loop
            self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Error starting bot: {str(e)}")
            return False
    
    def stop(self):
        """Stop the signal bot"""
        self.logger.info("Stopping Pocket Option Signal Bot...")
        self.is_running = False
        
        # Disconnect WebSocket
        self.api.disconnect_websocket()
        
        # Logout from API
        self.api.logout()
        
        self.logger.info("Bot stopped successfully")
    
    def _schedule_tasks(self):
        """Schedule recurring tasks"""
        # Generate signals every 5 minutes
        schedule.every(5).minutes.do(self._generate_signals_for_all_assets)
        
        # Update performance stats every hour
        schedule.every().hour.do(self._update_performance_stats)
        
        # Check open trades every minute
        schedule.every().minute.do(self._check_open_trades)
        
        # Daily cleanup at midnight
        schedule.every().day.at("00:00").do(self._daily_cleanup)
        
        self.logger.info("Scheduled tasks configured")
    
    def _main_loop(self):
        """Main bot loop"""
        self.logger.info("Bot main loop started")
        
        while self.is_running:
            try:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Check if market is open
                if self.api.is_market_open():
                    # Process any pending signals
                    self._process_pending_signals()
                
                # Sleep for a short interval
                time.sleep(10)
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                time.sleep(30)  # Wait before retrying
        
        self.stop()
    
    def _generate_signals_for_all_assets(self):
        """Generate signals for all configured assets"""
        if not self.api.is_market_open():
            self.logger.info("Market is closed, skipping signal generation")
            return
        
        self.logger.info("Generating signals for all assets...")
        
        for asset in self.config.TRADING_ASSETS:
            try:
                # Get market data
                market_data = self.api.get_market_data(asset, "5m", 200)
                
                if market_data and len(market_data.get('close', [])) >= 100:
                    # Convert to DataFrame
                    df = pd.DataFrame(market_data)
                    
                    # Generate signal
                    signal_analysis = self.signal_generator.generate_signal(asset, df)
                    final_signal = self.signal_generator.generate_final_signal(signal_analysis)
                    
                    # Store signal
                    self.active_signals[asset] = {
                        'signal': final_signal,
                        'analysis': signal_analysis,
                        'timestamp': datetime.now(),
                        'processed': False
                    }
                    
                    self.logger.info(f"Signal generated for {asset}: {final_signal['signal_type']} "
                                   f"(Confidence: {final_signal['confidence']:.2f})")
                else:
                    self.logger.warning(f"Insufficient market data for {asset}")
                    
            except Exception as e:
                self.logger.error(f"Error generating signal for {asset}: {str(e)}")
        
        self.logger.info(f"Signal generation completed. {len(self.active_signals)} signals active")
    
    def _process_pending_signals(self):
        """Process pending signals and execute trades"""
        for asset, signal_data in list(self.active_signals.items()):
            if signal_data['processed']:
                continue
            
            signal = signal_data['signal']
            
            # Only process high-confidence signals
            if signal['confidence'] < self.config.SIGNAL_CONFIDENCE_THRESHOLD:
                self.logger.info(f"Signal for {asset} below confidence threshold: {signal['confidence']:.2f}")
                signal_data['processed'] = True
                continue
            
            # Check if we should place a trade
            if self._should_place_trade(signal):
                self._execute_trade(asset, signal)
                signal_data['processed'] = True
            else:
                self.logger.info(f"Trade conditions not met for {asset}")
    
    def _should_place_trade(self, signal: Dict[str, Any]) -> bool:
        """Determine if a trade should be placed based on signal and risk management"""
        # Check if signal is actionable
        if signal['signal_type'] == 'NEUTRAL':
            return False
        
        # Check risk management rules
        risk_metrics = self.risk_manager.get_risk_metrics()
        
        if risk_metrics['remaining_trades'] <= 0:
            self.logger.warning("Daily trade limit reached")
            return False
        
        if risk_metrics['remaining_loss_limit'] <= 0:
            self.logger.warning("Daily loss limit reached")
            return False
        
        # Check if we have sufficient balance
        account_balance = self.api.get_account_balance()
        if account_balance < self.config.MIN_INVESTMENT:
            self.logger.warning("Insufficient account balance")
            return False
        
        return True
    
    def _execute_trade(self, asset: str, signal: Dict[str, Any]):
        """Execute a trade based on the signal"""
        try:
            self.logger.info(f"Executing trade for {asset}: {signal['signal_type']}")
            
            # Get account balance
            account_balance = self.api.get_account_balance()
            
            # Calculate position size
            position_info = self.risk_manager.calculate_position_size(
                signal, account_balance
            )
            
            if position_info['position_size'] <= 0:
                self.logger.warning(f"Cannot place trade for {asset}: {position_info.get('reason', 'Unknown')}")
                return
            
            # Place the trade
            trade_result = self.api.place_trade(
                asset=asset,
                direction=signal['direction'],
                amount=position_info['position_size'],
                expiry_time=self.config.EXPIRY_TIME
            )
            
            if trade_result:
                # Record the trade
                trade_record = {
                    'id': trade_result.get('id'),
                    'asset': asset,
                    'direction': signal['direction'],
                    'amount': position_info['position_size'],
                    'signal_confidence': signal['confidence'],
                    'entry_time': datetime.now(),
                    'expiry_time': datetime.now() + timedelta(minutes=self.config.EXPIRY_TIME),
                    'status': 'open',
                    'signal': signal,
                    'position_info': position_info
                }
                
                self.trade_history.append(trade_record)
                
                self.logger.info(f"Trade executed successfully: {trade_record['id']} for {asset}")
                
                # Update risk manager
                self.risk_manager.update_trade_result({
                    'profit_loss': 0,  # Will be updated when trade closes
                    'amount': position_info['position_size']
                })
            else:
                self.logger.error(f"Failed to execute trade for {asset}")
                
        except Exception as e:
            self.logger.error(f"Error executing trade for {asset}: {str(e)}")
    
    def _check_open_trades(self):
        """Check status of open trades"""
        for trade in self.trade_history:
            if trade['status'] != 'open':
                continue
            
            # Check if trade has expired
            if datetime.now() >= trade['expiry_time']:
                self._close_trade(trade)
    
    def _close_trade(self, trade: Dict[str, Any]):
        """Close a completed trade and calculate results"""
        try:
            # Get trade status from API
            trade_status = self.api.get_trade_status(trade['id'])
            
            if trade_status:
                # Calculate profit/loss
                if trade_status.get('status') == 'won':
                    profit_loss = trade['amount'] * 0.8  # Typical 80% payout
                    trade['status'] = 'won'
                    self.performance_stats['winning_trades'] += 1
                    self.performance_stats['total_profit'] += profit_loss
                else:
                    profit_loss = -trade['amount']  # Full loss
                    trade['status'] = 'lost'
                    self.performance_stats['losing_trades'] += 1
                    self.performance_stats['total_loss'] += abs(profit_loss)
                
                trade['profit_loss'] = profit_loss
                trade['close_time'] = datetime.now()
                trade['final_status'] = trade_status.get('status')
                
                # Update performance stats
                self.performance_stats['total_trades'] += 1
                self.performance_stats['win_rate'] = (
                    self.performance_stats['winning_trades'] / self.performance_stats['total_trades']
                )
                
                if self.performance_stats['total_loss'] > 0:
                    self.performance_stats['profit_factor'] = (
                        self.performance_stats['total_profit'] / self.performance_stats['total_loss']
                    )
                
                self.logger.info(f"Trade {trade['id']} closed: {trade['status']} "
                               f"(P&L: ${profit_loss:.2f})")
                
                # Update risk manager
                self.risk_manager.update_trade_result({
                    'profit_loss': profit_loss,
                    'amount': trade['amount']
                })
                
            else:
                self.logger.warning(f"Could not get status for trade {trade['id']}")
                
        except Exception as e:
            self.logger.error(f"Error closing trade {trade['id']}: {str(e)}")
    
    def _update_performance_stats(self):
        """Update and log performance statistics"""
        self.logger.info("=== PERFORMANCE STATISTICS ===")
        self.logger.info(f"Total Trades: {self.performance_stats['total_trades']}")
        self.logger.info(f"Win Rate: {self.performance_stats['win_rate']:.2%}")
        self.logger.info(f"Total Profit: ${self.performance_stats['total_profit']:.2f}")
        self.logger.info(f"Total Loss: ${self.performance_stats['total_loss']:.2f}")
        self.logger.info(f"Net P&L: ${self.performance_stats['total_profit'] - self.performance_stats['total_loss']:.2f}")
        self.logger.info(f"Profit Factor: {self.performance_stats['profit_factor']:.2f}")
        
        # Log risk metrics
        risk_metrics = self.risk_manager.get_risk_metrics()
        self.logger.info("=== RISK METRICS ===")
        self.logger.info(f"Daily Trades: {risk_metrics['daily_trades']}/{risk_metrics['max_daily_trades']}")
        self.logger.info(f"Daily Loss: ${risk_metrics['daily_loss']:.2f}/${risk_metrics['max_daily_loss']:.2f}")
        self.logger.info(f"Remaining Trades: {risk_metrics['remaining_trades']}")
        self.logger.info(f"Remaining Loss Limit: ${risk_metrics['remaining_loss_limit']:.2f}")
    
    def _daily_cleanup(self):
        """Perform daily cleanup tasks"""
        self.logger.info("Performing daily cleanup...")
        
        # Reset daily statistics
        self.risk_manager._reset_daily_stats_if_needed()
        
        # Archive old trade history (keep last 1000 trades)
        if len(self.trade_history) > 1000:
            self.trade_history = self.trade_history[-1000:]
        
        # Clear old signals
        current_time = datetime.now()
        for asset in list(self.active_signals.keys()):
            signal_age = current_time - self.active_signals[asset]['timestamp']
            if signal_age > timedelta(hours=1):
                del self.active_signals[asset]
        
        self.logger.info("Daily cleanup completed")
    
    def get_bot_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'is_authenticated': self.api.is_authenticated,
            'market_open': self.api.is_market_open(),
            'account_balance': self.api.get_account_balance(),
            'active_signals': len(self.active_signals),
            'open_trades': len([t for t in self.trade_history if t['status'] == 'open']),
            'total_trades': len(self.trade_history),
            'performance_stats': self.performance_stats,
            'risk_metrics': self.risk_manager.get_risk_metrics()
        }
    
    def save_trade_history(self, filename: str = None):
        """Save trade history to file"""
        if not filename:
            filename = f"trade_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            # Convert datetime objects to strings for JSON serialization
            serializable_history = []
            for trade in self.trade_history:
                trade_copy = trade.copy()
                if 'entry_time' in trade_copy:
                    trade_copy['entry_time'] = trade_copy['entry_time'].isoformat()
                if 'expiry_time' in trade_copy:
                    trade_copy['expiry_time'] = trade_copy['expiry_time'].isoformat()
                if 'close_time' in trade_copy:
                    trade_copy['close_time'] = trade_copy['close_time'].isoformat()
                serializable_history.append(trade_copy)
            
            with open(filename, 'w') as f:
                json.dump(serializable_history, f, indent=2)
            
            self.logger.info(f"Trade history saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving trade history: {str(e)}")

def main():
    """Main function to run the bot"""
    bot = PocketOptionSignalBot()
    
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.logger.info("Bot interrupted by user")
    except Exception as e:
        bot.logger.error(f"Bot error: {str(e)}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
