"""
Pocket Option Trading Bot
Integrates Telegram commands with Pocket Option trading
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from pocket_option_api import PocketOptionAPI
from config import BOT_TOKEN, POCKET_OPTION_EMAIL, POCKET_OPTION_PASSWORD, POCKET_OPTION_DEMO

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TradingBot:
    """Main trading bot class"""
    
    def __init__(self):
        self.pocket_api = None
        self.active_trades = {}
        self.trade_history = []
        self.user_sessions = {}
        
        # Initialize Pocket Option API
        self._init_pocket_option()
        
    def _init_pocket_option(self):
        """Initialize Pocket Option API connection"""
        try:
            self.pocket_api = PocketOptionAPI(
                email=POCKET_OPTION_EMAIL,
                password=POCKET_OPTION_PASSWORD,
                demo=POCKET_OPTION_DEMO
            )
            
            # Set up callbacks
            self.pocket_api.on_balance_update = self._on_balance_update
            self.pocket_api.on_trade_result = self._on_trade_result
            self.pocket_api.on_connection_status = self._on_connection_status
            
            logger.info("Pocket Option API initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pocket Option API: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Welcome message with trading options"""
        user = update.effective_user
        
        welcome_text = f"""
🚀 **Welcome to Pocket Option Trading Bot!**

Hi {user.mention_html()}! 👋

I'm your personal trading assistant that connects Telegram directly to Pocket Option.

**📊 Trading Commands:**
• `/balance` - Check account balance
• `/buy [asset] [time] [amount]` - Place a CALL trade
• `/sell [asset] [time] [amount]` - Place a PUT trade
• `/trades` - View active trades
• `/history` - Trading history
• `/status` - Connection status

**💡 Examples:**
• `/buy EURUSD 1m 10` - $10 CALL on EURUSD for 1 minute
• `/sell GBPUSD 5m 25` - $25 PUT on GBPUSD for 5 minutes

**⚙️ Other Commands:**
• `/help` - Full command list
• `/connect` - Connect to Pocket Option
• `/disconnect` - Disconnect from Pocket Option

**🔗 Status:** {'🟢 Connected' if self.pocket_api and self.pocket_api.is_connected() else '🔴 Disconnected'}
        """
        
        # Create inline keyboard for quick actions
        keyboard = [
            [
                InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
                InlineKeyboardButton("📊 View Trades", callback_data="trades")
            ],
            [
                InlineKeyboardButton("🔗 Connect", callback_data="connect"),
                InlineKeyboardButton("📈 Status", callback_data="status")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show comprehensive help"""
        help_text = """
📚 **Trading Bot Commands Guide**

**🚀 Trading Commands:**
• `/buy [asset] [time] [amount]` - Place CALL trade
• `/sell [asset] [time] [amount]` - Place PUT trade
• `/balance` - Check account balance
• `/trades` - View active trades
• `/history` - Trading history

**⚙️ System Commands:**
• `/connect` - Connect to Pocket Option
• `/disconnect` - Disconnect from Pocket Option
• `/status` - Connection and system status
• `/help` - Show this help

**📊 Trading Examples:**
• `/buy EURUSD 1m 10` - $10 CALL on EURUSD for 1 minute
• `/sell GBPUSD 5m 25` - $25 PUT on GBPUSD for 5 minutes
• `/buy BTCUSD 15m 50` - $50 CALL on Bitcoin for 15 minutes

**⏱️ Time Formats:**
• `1m` = 1 minute
• `5m` = 5 minutes
• `15m` = 15 minutes
• `1h` = 1 hour
• `4h` = 4 hours
• `1d` = 1 day

**💡 Tips:**
• Always check your balance before trading
• Start with small amounts to test
• Monitor your active trades
• Use demo mode for practice
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def connect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Connect to Pocket Option"""
        if not self.pocket_api:
            await update.message.reply_text("❌ Pocket Option API not initialized!")
            return
        
        try:
            if self.pocket_api.connect():
                status = self.pocket_api.get_connection_status()
                response = f"""
🔗 **Connected to Pocket Option!**

**Status:** 🟢 Connected
**Balance:** ${status['balance']:.2f}
**Assets Available:** {status['assets_count']}
**Session ID:** {status['session_id'][:8]}...

You can now place trades using:
• `/buy [asset] [time] [amount]`
• `/sell [asset] [time] [amount]`
                """
                await update.message.reply_text(response, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Failed to connect to Pocket Option. Check your credentials.")
        except Exception as e:
            await update.message.reply_text(f"❌ Connection error: {str(e)}")
    
    async def disconnect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Disconnect from Pocket Option"""
        if self.pocket_api:
            self.pocket_api.disconnect()
            await update.message.reply_text("🔌 Disconnected from Pocket Option")
        else:
            await update.message.reply_text("❌ Not connected to Pocket Option")
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check account balance"""
        if not self.pocket_api or not self.pocket_api.is_connected():
            await update.message.reply_text("❌ Not connected to Pocket Option. Use `/connect` first.")
            return
        
        balance = self.pocket_api.get_balance()
        response = f"""
💰 **Account Balance**

**Current Balance:** ${balance:.2f}
**Status:** 🟢 Connected
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Quick Actions:**
• Use `/buy` or `/sell` to place trades
• Check `/trades` for active positions
• View `/history` for past trades
        """
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Place a CALL trade"""
        await self._place_trade(update, context, "call")
    
    async def sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Place a PUT trade"""
        await self._place_trade(update, context, "put")
    
    async def _place_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE, direction: str):
        """Place a trade (internal method)"""
        if not self.pocket_api or not self.pocket_api.is_connected():
            await update.message.reply_text("❌ Not connected to Pocket Option. Use `/connect` first.")
            return
        
        if len(context.args) < 3:
            await update.message.reply_text(
                f"❌ **Invalid {direction.upper()} command format:**\n\n"
                f"**Correct format:** /{direction} [asset] [time] [amount]\n\n"
                f"**Examples:**\n"
                f"• /{direction} EURUSD 1m 10\n"
                f"• /{direction} GBPUSD 5m 25\n"
                f"• /{direction} BTCUSD 15m 50",
                parse_mode='Markdown'
            )
            return
        
        try:
            asset = context.args[0].upper()
            time_str = context.args[1]
            amount = float(context.args[2])
            
            # Parse time
            expiry = self._parse_time(time_str)
            if not expiry:
                await update.message.reply_text(
                    "❌ **Invalid time format:**\n\n"
                    "**Valid formats:** 1m, 5m, 15m, 1h, 4h, 1d\n\n"
                    f"**Example:** /{direction} {asset} 5m {amount}"
                )
                return
            
            # Check balance
            balance = self.pocket_api.get_balance()
            if amount > balance:
                await update.message.reply_text(
                    f"❌ **Insufficient balance:**\n\n"
                    f"**Required:** ${amount:.2f}\n"
                    f"**Available:** ${balance:.2f}\n"
                    f"**Shortfall:** ${amount - balance:.2f}"
                )
                return
            
            # Place trade
            trade_result = self.pocket_api.place_trade(
                asset=asset,
                amount=amount,
                direction=direction,
                expiry=expiry,
                strategy="telegram_bot"
            )
            
            if trade_result.get("success"):
                # Store trade info
                trade_id = trade_result.get("trade_id", f"trade_{len(self.active_trades)}")
                self.active_trades[trade_id] = trade_result
                
                response = f"""
✅ **{direction.upper()} Trade Placed Successfully!**

**Trade ID:** {trade_id}
**Asset:** {asset}
**Direction:** {direction.upper()}
**Amount:** ${amount:.2f}
**Expiry:** {time_str} ({expiry} seconds)
**Entry Price:** {trade_result.get('entry_price', 'N/A')}
**Strategy:** Telegram Bot
**Timestamp:** {datetime.fromtimestamp(trade_result['timestamp']/1000).strftime('%H:%M:%S')}

**Status:** 🟢 Active
**Balance Remaining:** ${balance - amount:.2f}

**Monitor your trade with:** `/trades`
                """
                
                # Create inline keyboard for trade management
                keyboard = [
                    [
                        InlineKeyboardButton("📊 View All Trades", callback_data="trades"),
                        InlineKeyboardButton("💰 Check Balance", callback_data="balance")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
                
            else:
                await update.message.reply_text(
                    f"❌ **Trade placement failed:**\n\n"
                    f"**Error:** {trade_result.get('error', 'Unknown error')}\n\n"
                    f"**Please try again or check your connection.**"
                )
                
        except ValueError:
            await update.message.reply_text(
                f"❌ **Invalid amount:** Please enter a valid number.\n\n"
                f"**Example:** /{direction} {context.args[0]} {context.args[1]} 10"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ **Error placing trade:** {str(e)}")
    
    def _parse_time(self, time_str: str) -> Optional[int]:
        """Parse time string to seconds"""
        try:
            if time_str.endswith('m'):
                return int(time_str[:-1]) * 60
            elif time_str.endswith('h'):
                return int(time_str[:-1]) * 3600
            elif time_str.endswith('d'):
                return int(time_str[:-1]) * 86400
            else:
                return None
        except:
            return None
    
    async def trades_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """View active trades"""
        if not self.active_trades:
            await update.message.reply_text("📊 **No Active Trades**\n\nYou don't have any open positions at the moment.")
            return
        
        response = "📊 **Active Trades:**\n\n"
        for trade_id, trade in self.active_trades.items():
            response += f"""
**Trade ID:** {trade_id}
**Asset:** {trade['asset']}
**Direction:** {trade['direction'].upper()}
**Amount:** ${trade['amount']:.2f}
**Expiry:** {trade['expiry']} seconds
**Strategy:** {trade['strategy']}
**Entry Time:** {datetime.fromtimestamp(trade['timestamp']/1000).strftime('%H:%M:%S')}
---
            """
        
        response += "\n**Total Active Trades:** " + str(len(self.active_trades))
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
                InlineKeyboardButton("📈 View Status", callback_data="status")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """View trading history"""
        if not self.pocket_api:
            await update.message.reply_text("❌ Pocket Option API not initialized!")
            return
        
        trades = self.pocket_api.get_trades()
        if not trades:
            await update.message.reply_text("📈 **No Trading History**\n\nYou haven't placed any trades yet.")
            return
        
        response = "📈 **Recent Trading History:**\n\n"
        for i, trade in enumerate(trades[-5:], 1):  # Show last 5 trades
            response += f"""
**Trade {i}:**
**Asset:** {trade.get('asset', 'N/A')}
**Direction:** {trade.get('direction', 'N/A').upper()}
**Amount:** ${trade.get('amount', 0):.2f}
**Result:** {trade.get('result', 'N/A')}
**Profit/Loss:** ${trade.get('profit', 0):.2f}
---
            """
        
        response += f"\n**Total Trades:** {len(trades)}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show bot and connection status"""
        if not self.pocket_api:
            status_text = """
📊 **Bot Status Report**

**Bot Status:** 🟢 Running
**Pocket Option:** ❌ Not Initialized
**Version:** 1.0.0

**Available Commands:** 8
**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        else:
            status = self.pocket_api.get_connection_status()
            status_text = f"""
📊 **Bot Status Report**

**Bot Status:** 🟢 Running
**Pocket Option:** {'🟢 Connected' if status['connected'] else '🔴 Disconnected'}
**Version:** 1.0.0

**Connection Details:**
• **Status:** {'🟢 Connected' if status['connected'] else '🔴 Disconnected'}
• **Balance:** ${status['balance']:.2f}
• **Assets Available:** {status['assets_count']}
• **Active Trades:** {len(self.active_trades)}
• **Total Trades:** {status['trades_count']}

**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "balance":
            await self.balance_command(update, context)
        elif query.data == "trades":
            await self.trades_command(update, context)
        elif query.data == "connect":
            await self.connect_command(update, context)
        elif query.data == "status":
            await self.status_command(update, context)
    
    # Callback methods for Pocket Option API
    def _on_balance_update(self, new_balance: float):
        """Handle balance updates from Pocket Option"""
        logger.info(f"Balance updated: ${new_balance:.2f}")
    
    def _on_trade_result(self, trade_result: Dict[str, Any]):
        """Handle trade results from Pocket Option"""
        logger.info(f"Trade result received: {trade_result}")
        # Remove from active trades if completed
        trade_id = trade_result.get('trade_id')
        if trade_id in self.active_trades:
            del self.active_trades[trade_id]
    
    def _on_connection_status(self, status: Dict[str, Any]):
        """Handle connection status updates"""
        logger.info(f"Connection status: {status}")

def main():
    """Initialize and start the trading bot"""
    # Create bot instance
    trading_bot = TradingBot()
    
    # Create Telegram application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", trading_bot.start_command))
    application.add_handler(CommandHandler("help", trading_bot.help_command))
    application.add_handler(CommandHandler("connect", trading_bot.connect_command))
    application.add_handler(CommandHandler("disconnect", trading_bot.disconnect_command))
    application.add_handler(CommandHandler("balance", trading_bot.balance_command))
    application.add_handler(CommandHandler("buy", trading_bot.buy_command))
    application.add_handler(CommandHandler("sell", trading_bot.sell_command))
    application.add_handler(CommandHandler("trades", trading_bot.trades_command))
    application.add_handler(CommandHandler("history", trading_bot.history_command))
    application.add_handler(CommandHandler("status", trading_bot.status_command))
    
    # Add callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(trading_bot.button_callback))
    
    # Start the bot
    print("🚀 Starting Pocket Option Trading Bot...")
    print("📱 Bot is now running and listening for trading commands!")
    print("🔧 Available commands: /start, /help, /buy, /sell, /balance, /trades, /status")
    print("⏹️  Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
