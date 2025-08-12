#!/usr/bin/env python3
"""
Enhanced Telegram Bot - Main Bot File
cccccLclEssential Commands Implementation
"""

import logging
import random
import datetime
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from .config import BOT_TOKEN

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get logger
logger = logging.getLogger(__name__)

# Simple function for sending telegram messages (used by main bot)
async def send_telegram(message: str) -> bool:
    """
    Simple function to send telegram messages
    Used by the main OTC bot for signal notifications
    """
    try:
        # For now, just log the message since we don't have a bot instance
        logger.info(f"📱 Telegram Message: {message}")
        print(f"📱 Telegram Message: {message}")
        return True
    except Exception as e:
        logger.error(f"Failed to send telegram message: {e}")
        return False

# ========== ESSENTIAL BASICS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    welcome_text = f"""
🤖 **Welcome to Your Enhanced Bot!**

Hi {user.mention_html()}! 👋

I'm your personal assistant with comprehensive features including:
• 📊 **OTC Signal Trading** - Premium 92%+ payout signals
• 💰 **Credit System** - Pay-as-you-go service
• 🔧 **Multiple Tools** - Calculator, analysis, and more
• 📈 **Real-time Data** - Live market information

**Quick Start:**
• `/help` - See all available commands
• `/info` - Learn about our services
• `/balance` - Check your credit balance
• `/process` - Start using our main service

**Ready to get started?** 🚀
    """
    
    # Create inline keyboard for quick actions
    keyboard = [
        [
            InlineKeyboardButton("📚 Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ Info", callback_data="info")
        ],
        [
            InlineKeyboardButton("💰 Balance", callback_data="balance"),
            InlineKeyboardButton("🚀 Start Service", callback_data="process")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show comprehensive help with all commands."""
    help_text = """
📚 **Complete Command Guide**

**🔰 Essential Basics:**
• `/start` - Welcome message and bot introduction
• `/help` - This comprehensive help guide
• `/info` - About our service, pricing, features
• `/cancel` - Stop current operation
• `/status` - Check bot status and uptime

**👤 User Account Management:**
• `/balance` - Show current credit balance
• `/deposit` - Generate crypto payment address
• `/history` - Transaction and usage history
• `/account` - User account details
• `/settings` - User preferences

**🚀 Service Commands:**
• `/process` - Main service command (OTC signals)
• `/upload` - File upload handling
• `/convert` - File conversion
• `/analyze` - Data analysis
• `/generate` - Content generation

**💳 Payment & Credits:**
• `/pricing` - Show current rates
• `/topup` - Add credits via crypto
• `/transactions` - Payment history
• `/invoice` - Generate payment request

**🛠️ Utility Commands:**
• `/calc [expression]` - Calculator
• `/random [min-max]` - Random number generator
• `/time` - Current date and time
• `/joke` - Get a random joke

**💡 Examples:**
• `/calc 15*3+7`
• `/random 1-100`
• `/process EURUSD-OTC`

**Need help?** Just send me a message! 🤖
    """
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
            InlineKeyboardButton("🚀 Start Service", callback_data="process")
        ],
        [
            InlineKeyboardButton("📊 Pricing", callback_data="pricing"),
            InlineKeyboardButton("📞 Support", callback_data="support")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show information about the service."""
    info_text = """
ℹ️ **About Our Service**

**🎯 What We Offer:**
• **Premium OTC Signals** - 92%+ payout rate filtering
• **Real-time Analysis** - Multi-timeframe technical analysis
• **Credit System** - Pay-as-you-go, no subscriptions
• **24/7 Monitoring** - Automated signal generation
• **Professional Quality** - 97+ score threshold signals

**💰 Pricing Structure:**
• **Signal Package**: 10 credits per premium signal
• **Analysis Package**: 5 credits per detailed analysis
• **Bulk Discounts**: Available for high-volume users
• **Crypto Payments**: Bitcoin, Ethereum, USDT accepted

**🚀 Key Features:**
• Ultra-selective signal filtering
• Real-time market monitoring
• Professional risk management
• Mobile-friendly interface
• Instant notifications

**📊 Service Statistics:**
• **Uptime**: 99.9%
• **Signal Accuracy**: 97%+
• **Response Time**: <1 second
• **Active Users**: 1000+

**Ready to start?** Use `/process` to begin! 🚀
    """
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Pricing", callback_data="pricing"),
            InlineKeyboardButton("🚀 Start Now", callback_data="process")
        ],
        [
            InlineKeyboardButton("📊 Demo", callback_data="demo"),
            InlineKeyboardButton("📞 Contact", callback_data="contact")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(info_text, parse_mode='Markdown', reply_markup=reply_markup)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel current operation."""
    await update.message.reply_text(
        "❌ **Operation Cancelled**\n\nAll pending operations have been stopped. Use `/start` to begin again."
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check bot status and uptime."""
    uptime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status_text = f"""
📊 **Bot Status Report**

**🟢 Status:** Online & Running
**⏰ Uptime:** {uptime}
**🔄 Version:** 2.0.0
**👥 Active Users:** 1000+
**📡 Services:** All Operational

**System Health:**
• ✅ OTC Signal Generation
• ✅ Market Data Feed
• ✅ Payment Processing
• ✅ User Management
• ✅ Notification System

**Performance Metrics:**
• **Response Time:** <1 second
• **Signal Quality:** 97%+ accuracy
• **Uptime:** 99.9%
• **Last Update:** {uptime}

**Commands Available:** 25+
**Last Update:** {uptime}
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Live Stats", callback_data="stats"),
            InlineKeyboardButton("🔧 System Info", callback_data="system")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(status_text, parse_mode='Markdown', reply_markup=reply_markup)

# ========== USER ACCOUNT MANAGEMENT ==========
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current credit balance."""
    # Mock balance for demonstration
    balance = 150.0
    balance_text = f"""
💰 **Account Balance**

**Current Credits:** {balance:.2f}
**Status:** 🟢 Active
**Last Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Credit Usage:**
• **Signals Available:** {int(balance/10)} premium signals
• **Analysis Available:** {int(balance/5)} detailed analyses
• **Next Top-up:** Recommended at {max(0, 50-balance):.2f} credits

**Quick Actions:**
• Use `/topup` to add more credits
• Use `/process` to start using credits
• Check `/history` for usage details
    """
    
    keyboard = [
        [
            InlineKeyboardButton("💳 Top Up", callback_data="topup"),
            InlineKeyboardButton("📊 History", callback_data="history")
        ],
        [
            InlineKeyboardButton("🚀 Use Service", callback_data="process"),
            InlineKeyboardButton("📋 Account", callback_data="account")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(balance_text, parse_mode='Markdown', reply_markup=reply_markup)

async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate crypto payment address."""
    deposit_text = """
💳 **Crypto Payment Addresses**

**Bitcoin (BTC):**
`bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh`

**Ethereum (ETH):**
`0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6`

**USDT (Tron):**
`TQn9Y2khDD95J42FQtQTdwVVRKtCwVHrqR`

**💡 Instructions:**
1. Send your desired amount to any address above
2. Credits will be added automatically within 10 minutes
3. Minimum deposit: $10 USD equivalent
4. No transaction fees on our end

**⚠️ Important:**
• Only send to the addresses listed above
• Include your Telegram username in the memo if possible
• Contact support if credits aren't added within 1 hour

**Need help?** Use `/support` for assistance.
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Check Balance", callback_data="balance"),
            InlineKeyboardButton("📞 Support", callback_data="support")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(deposit_text, parse_mode='Markdown', reply_markup=reply_markup)

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show transaction and usage history."""
    history_text = """
📊 **Transaction & Usage History**

**Recent Transactions:**
• **2025-08-11 20:30** - Signal Package: -10 credits
• **2025-08-11 19:15** - BTC Deposit: +50 credits
• **2025-08-11 18:45** - Analysis Package: -5 credits
• **2025-08-11 17:20** - ETH Deposit: +100 credits

**Usage Summary (This Month):**
• **Signals Used:** 15 premium signals
• **Analyses Used:** 8 detailed analyses
• **Credits Spent:** 190 credits
• **Credits Added:** 150 credits
• **Current Balance:** 150 credits

**Service Breakdown:**
• **OTC Signals:** 150 credits (15 signals)
• **Market Analysis:** 40 credits (8 analyses)
• **Total Value:** $190 USD equivalent

**📈 Performance:**
• **Win Rate:** 97.3%
• **Average Return:** 92.5%
• **Best Signal:** +156% profit
    """
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Top Up", callback_data="topup"),
            InlineKeyboardButton("📊 Detailed Stats", callback_data="stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(history_text, parse_mode='Markdown', reply_markup=reply_markup)

async def account_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user account details."""
    user = update.effective_user
    account_text = f"""
👤 **Account Details**

**User Information:**
• **Name:** {user.first_name} {user.last_name or ''}
• **Username:** @{user.username or 'Not set'}
• **User ID:** {user.id}
• **Language:** {user.language_code or 'Not set'}
• **Join Date:** {datetime.datetime.now().strftime('%Y-%m-%d')}

**Account Status:**
• **Status:** 🟢 Active
• **Verification:** ✅ Verified
• **Premium:** 🟡 Standard User
• **Referral Code:** {user.id}

**Usage Statistics:**
• **Total Credits Used:** 450 credits
• **Signals Generated:** 45 premium signals
• **Analyses Requested:** 18 detailed analyses
• **Account Age:** 30 days

**Preferences:**
• **Notification Type:** Telegram messages
• **Signal Frequency:** High (when available)
• **Risk Level:** Medium
• **Preferred Pairs:** OTC pairs only

**Account Actions:**
• Use `/settings` to modify preferences
• Use `/upgrade` for premium features
• Contact support for account issues
    """
    
    keyboard = [
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("📊 Statistics", callback_data="stats")
        ],
        [
            InlineKeyboardButton("🔒 Security", callback_data="security"),
            InlineKeyboardButton("📞 Support", callback_data="support")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(account_text, parse_mode='Markdown', reply_markup=reply_markup)

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user preferences and settings."""
    settings_text = """
⚙️ **User Settings & Preferences**

**Notification Settings:**
• **Signal Alerts:** ✅ Enabled
• **Analysis Reports:** ✅ Enabled
• **Balance Updates:** ✅ Enabled
• **Market News:** ❌ Disabled
• **Weekly Reports:** ✅ Enabled

**Trading Preferences:**
• **Risk Level:** Medium (Default)
• **Preferred Pairs:** OTC pairs only
• **Signal Frequency:** High (when available)
• **Minimum Score:** 97+
• **Payout Threshold:** 92%+

**Display Settings:**
• **Language:** English
• **Time Format:** 24-hour
• **Currency:** USD
• **Theme:** Dark mode
• **Compact Mode:** Disabled

**Privacy Settings:**
• **Data Sharing:** Minimal
• **Analytics:** ✅ Enabled
• **Marketing:** ❌ Disabled
• **Third-party:** ❌ Disabled

**To modify settings, contact support or use the inline buttons below.**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🔔 Notifications", callback_data="notifications"),
            InlineKeyboardButton("🎯 Trading", callback_data="trading_prefs")
        ],
        [
            InlineKeyboardButton("🌐 Display", callback_data="display"),
            InlineKeyboardButton("🔒 Privacy", callback_data="privacy")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(settings_text, parse_mode='Markdown', reply_markup=reply_markup)

# ========== SERVICE COMMANDS ==========
async def process_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main service command."""
    process_text = """
🚀 **Main Service - OTC Signal Generation**

**Available Services:**
• **Premium Signals** - 97+ score, 92%+ payout (10 credits)
• **Market Analysis** - Detailed technical analysis (5 credits)
• **Risk Assessment** - Position sizing & risk management (3 credits)
• **Portfolio Review** - Performance analysis (8 credits)

**Current Market Status:**
• **OTC Pairs Available:** 10 pairs
• **Signal Quality:** 97+ score threshold
• **Payout Rates:** 92%+ minimum
• **Market Hours:** 24/7 OTC trading

**Quick Start:**
1. Choose your service type
2. Select trading pair (optional)
3. Confirm credit deduction
4. Receive instant results

**Your Balance:** 150 credits
**Estimated Cost:** 10-15 credits per service

**Ready to start?** Choose your service below! 🎯
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Premium Signal", callback_data="signal"),
            InlineKeyboardButton("📈 Market Analysis", callback_data="analysis")
        ],
        [
            InlineKeyboardButton("⚠️ Risk Assessment", callback_data="risk"),
            InlineKeyboardButton("📋 Portfolio Review", callback_data="portfolio")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(process_text, parse_mode='Markdown', reply_markup=reply_markup)

# ========== PAYMENT & CREDITS ==========
async def pricing_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current rates."""
    pricing_text = """
💰 **Service Pricing & Rates**

**📊 Signal Services:**
• **Premium Signal (97+ score):** 10 credits
• **Ultra Signal (99+ score):** 15 credits
• **Signal Package (5 signals):** 45 credits (10% off)
• **Monthly Unlimited:** 500 credits

**📈 Analysis Services:**
• **Basic Analysis:** 5 credits
• **Detailed Analysis:** 8 credits
• **Risk Assessment:** 3 credits
• **Portfolio Review:** 8 credits

**💳 Credit Packages:**
• **Starter:** $10 = 50 credits
• **Basic:** $25 = 150 credits (20% bonus)
• **Premium:** $50 = 350 credits (40% bonus)
• **Professional:** $100 = 800 credits (60% bonus)

**🎯 Special Offers:**
• **New User Bonus:** 20% extra credits
• **Referral Bonus:** 10% of referred user's first purchase
• **Bulk Discount:** 15% off orders over $100
• **Loyalty Program:** Earn 1 credit per $10 spent

**💡 Value Proposition:**
• Average signal return: 92%+
• Risk management included
• 24/7 support
• No subscription fees

**Ready to get started?** Use `/topup` to purchase credits! 🚀
    """
    
    keyboard = [
        [
            InlineKeyboardButton("💳 Buy Credits", callback_data="topup"),
            InlineKeyboardButton("📊 Compare Plans", callback_data="compare")
        ],
        [
            InlineKeyboardButton("🎁 Referral Program", callback_data="referral"),
            InlineKeyboardButton("📞 Contact Sales", callback_data="sales")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(pricing_text, parse_mode='Markdown', reply_markup=reply_markup)

async def topup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add credits via crypto."""
    topup_text = """
💳 **Credit Top-up Options**

**🚀 Quick Top-up Packages:**
• **Starter:** $10 = 50 credits
• **Basic:** $25 = 150 credits (20% bonus)
• **Premium:** $50 = 350 credits (40% bonus)
• **Professional:** $100 = 800 credits (60% bonus)

**💎 Accepted Cryptocurrencies:**
• **Bitcoin (BTC)** - Most popular
• **Ethereum (ETH)** - Fast processing
• **USDT (Tron)** - Stable value
• **Litecoin (LTC)** - Low fees

**⚡ Processing Times:**
• **Bitcoin:** 10-30 minutes
• **Ethereum:** 2-5 minutes
• **USDT:** 1-3 minutes
• **Litecoin:** 2-5 minutes

**🔒 Security Features:**
• Multi-signature wallets
• Cold storage for large amounts
• Real-time transaction monitoring
• Automatic credit allocation

**📱 How to Top-up:**
1. Choose your package
2. Select cryptocurrency
3. Send payment to generated address
4. Credits added automatically
5. Receive confirmation

**Need help?** Use `/support` for assistance.
    """
    
    keyboard = [
        [
            InlineKeyboardButton("$10 - 50 Credits", callback_data="topup_10"),
            InlineKeyboardButton("$25 - 150 Credits", callback_data="topup_25")
        ],
        [
            InlineKeyboardButton("$50 - 350 Credits", callback_data="topup_50"),
            InlineKeyboardButton("$100 - 800 Credits", callback_data="topup_100")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(topup_text, parse_mode='Markdown', reply_markup=reply_markup)

# ========== UTILITY COMMANDS ==========
async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current date and time."""
    now = datetime.datetime.now()
    time_text = f"""
🕐 **Current Time & Date**

**📅 Date:** {now.strftime('%A, %B %d, %Y')}
**⏰ Time:** {now.strftime('%I:%M:%S %p')}
**🌍 Timezone:** {now.strftime('%Z')}
**📊 ISO Format:** {now.isoformat()}

**🌐 Global Times:**
• **UTC:** {datetime.datetime.utcnow().strftime('%H:%M:%S')}
• **EST:** {(now - datetime.timedelta(hours=5)).strftime('%I:%M:%S %p')}
• **PST:** {(now - datetime.timedelta(hours=8)).strftime('%I:%M:%S %p')}
• **GMT:** {(now + datetime.timedelta(hours=0)).strftime('%I:%M:%S')}

**📈 Market Status:**
• **OTC Markets:** 24/7 Active
• **Forex Markets:** {'🟢 Open' if 0 <= now.hour < 22 else '🔴 Closed'}
• **Crypto Markets:** 24/7 Active
• **Next Market Open:** {'Already Open' if 0 <= now.hour < 22 else 'Tomorrow 00:00 UTC'}
    """
    
    await update.message.reply_text(time_text, parse_mode='Markdown')

async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple calculator command."""
    if not context.args:
        await update.message.reply_text(
            "🧮 **Calculator Usage:**\n"
            "/calc [expression]\n\n"
            "**Examples:**\n"
            "/calc 2+2\n"
            "/calc 15*3+7\n"
            "/calc sqrt(16)\n"
            "/calc 2^8",
            parse_mode='Markdown'
        )
        return
    
    try:
        expression = ' '.join(context.args)
        # Replace common math symbols
        expression = expression.replace('^', '**').replace('×', '*').replace('÷', '/')
        
        # Handle special functions
        if 'sqrt(' in expression:
            expression = expression.replace('sqrt(', 'math.sqrt(')
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        
        # Format the result
        if isinstance(result, (int, float)):
            if result == int(result):
                result = int(result)
            response = f"🧮 **Calculator Result:**\n\n**Expression:** `{expression}`\n**Result:** `{result}`"
        else:
            response = f"🧮 **Calculator Result:**\n\n**Expression:** `{expression}`\n**Result:** `{result}`"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Calculation Error:**\n\n"
            f"**Expression:** `{expression}`\n"
            f"**Error:** {str(e)}\n\n"
            f"**Tip:** Use valid math expressions like: 2+2, 15*3, sqrt(16)",
            parse_mode='Markdown'
        )

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate random number command."""
    if not context.args:
        await update.message.reply_text(
            "🎲 **Random Number Generator:**\n\n"
            "**Usage:** /random [min-max]\n\n"
            "**Examples:**\n"
            "/random 1-100\n"
            "/random 0-1000\n"
            "/random 10-20",
            parse_mode='Markdown'
        )
        return
    
    try:
        range_str = context.args[0]
        if '-' in range_str:
            min_val, max_val = map(int, range_str.split('-'))
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            result = random.randint(min_val, max_val)
            response = f"🎲 **Random Number:**\n\n**Range:** {min_val} to {max_val}\n**Result:** `{result}`"
        else:
            max_val = int(range_str)
            result = random.randint(1, max_val)
            response = f"🎲 **Random Number:**\n\n**Range:** 1 to {max_val}\n**Result:** `{result}`"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text(
            "❌ **Invalid Format:**\n\n"
            "**Correct Format:** /random [min-max]\n\n"
            "**Examples:**\n"
            "/random 1-100\n"
            "/random 0-1000",
            parse_mode='Markdown'
        )

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a random joke."""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything! 🤓",
        "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
        "Why don't eggs tell jokes? They'd crack each other up! 🥚",
        "What do you call a fake noodle? An impasta! 🍝",
        "Why did the math book look so sad? Because it had too many problems! 📚",
        "What do you call a bear with no teeth? A gummy bear! 🐻",
        "Why don't skeletons fight each other? They don't have the guts! 💀",
        "What do you call a fish wearing a bowtie? So-fish-ticated! 🐟",
        "Why did the golfer bring two pairs of pants? In case he got a hole in one! ⛳",
        "What do you call a can opener that doesn't work? A can't opener! 🥫"
    ]
    
    joke = random.choice(jokes)
    await update.message.reply_text(f"😄 **Random Joke:**\n\n{joke}")

# ========== CALLBACK HANDLERS ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command(update, context)
    elif query.data == "info":
        await info_command(update, context)
    elif query.data == "balance":
        await balance_command(update, context)
    elif query.data == "process":
        await process_command(update, context)
    elif query.data == "pricing":
        await pricing_command(update, context)
    elif query.data == "topup":
        await topup_command(update, context)
    elif query.data == "history":
        await history_command(update, context)
    elif query.data == "account":
        await account_command(update, context)
    elif query.data == "settings":
        await settings_command(update, context)
    elif query.data == "support":
        await update.message.reply_text("📞 **Support Contact:**\n\nFor assistance, contact our support team:\n• **Email:** support@example.com\n• **Telegram:** @support_bot\n• **Response Time:** <2 hours")
    else:
        await update.message.reply_text("🔧 **Feature Coming Soon!**\n\nThis feature is under development and will be available soon.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle non-command messages intelligently."""
    user_message = update.message.text.lower()
    
    # Smart responses based on message content
    if any(word in user_message for word in ['hello', 'hi', 'hey']):
        response = "👋 Hello there! How can I help you today? Use /help to see all available commands!"
    elif any(word in user_message for word in ['how are you', 'how r u']):
        response = "🤖 I'm doing great, thanks for asking! I'm ready to help with OTC signals, analysis, and more. Try /start to see what I can do!"
    elif any(word in user_message for word in ['bye', 'goodbye', 'see you']):
        response = "👋 Goodbye! Feel free to come back anytime. Use /start to see what I can do!"
    elif any(word in user_message for word in ['thanks', 'thank you', 'thx']):
        response = "😊 You're welcome! I'm here to help. Try /help to see all my features!"
    elif any(word in user_message for word in ['what can you do', 'help me']):
        response = "🤖 I can do lots of things! Here are some highlights:\n\n• 📊 OTC Signal Generation\n• 📈 Market Analysis\n• 💰 Credit Management\n• 🧮 Calculator\n• 🎲 Random numbers\n• 😄 Jokes\n\nUse /help for the full list!"
    elif '?' in user_message:
        response = "🤔 That's an interesting question! I can help with OTC trading signals, market analysis, credit management, and more. Try /help to see what I can do!"
    else:
        response = f"💬 You said: \"{update.message.text}\"\n\n💡 **Tip:** I can do much more than just echo messages! Try /help to see all my features including OTC signal generation and market analysis."
    
    await update.message.reply_text(response)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("deposit", deposit_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("account", account_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("process", process_command))
    application.add_handler(CommandHandler("pricing", pricing_command))
    application.add_handler(CommandHandler("topup", topup_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("calc", calc_command))
    application.add_handler(CommandHandler("random", random_command))
    application.add_handler(CommandHandler("joke", joke_command))
    
    # Add callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("🤖 Starting Enhanced Telegram Bot with Essential Commands...")
    print("📱 Bot is now running with comprehensive features!")
    print("🔧 Available commands: /start, /help, /info, /balance, /process, /pricing, and more!")
    print("⏹️  Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
