#!/usr/bin/env python3
"""
Enhanced Telegram Bot - Main Bot File
"""

import logging
import random
import datetime
import math
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_text = f"""
🤖 **Welcome to Your Enhanced Bot!**

Hi {user.mention_html()}! 👋

I'm your personal assistant with lots of useful features.

**Quick Commands:**
• `/help` - Show all commands
• `/time` - Current time
• `/calc 2+2` - Calculator
• `/random 1-100` - Random number
• `/weather` - Weather info (coming soon)
• `/joke` - Get a random joke

**Just send me a message and I'll respond!**
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🤖 **Available Commands:**

**Basic Commands:**
/start - Start the bot
/help - Show this help message
/status - Check bot status

**Utility Commands:**
/time - Show current date and time
/calc [expression] - Calculator (e.g., /calc 2+2*3)
/random [min-max] - Random number generator (e.g., /random 1-100)
/joke - Get a random joke
/coin - Flip a coin
/dice - Roll a dice

**Examples:**
/calc 15*3+7
/random 1-1000
/time

**Message Handling:**
Send any text message and I'll respond intelligently!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current date and time."""
    now = datetime.datetime.now()
    time_text = f"""
🕐 **Current Time:**

**Date:** {now.strftime('%A, %B %d, %Y')}
**Time:** {now.strftime('%I:%M:%S %p')}
**Timezone:** {now.strftime('%Z')}

**ISO Format:** {now.isoformat()}
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

async def coin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Flip a coin."""
    result = random.choice(["Heads", "Tails"])
    emoji = "🪙" if result == "Heads" else "🪙"
    await update.message.reply_text(f"{emoji} **Coin Flip:**\n\n**Result:** {result}")

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Roll a dice."""
    result = random.randint(1, 6)
    dice_emoji = "🎲"
    await update.message.reply_text(f"{dice_emoji} **Dice Roll:**\n\n**Result:** {result}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check bot status."""
    uptime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status_text = f"""
✅ **Bot Status Report**

**Status:** 🟢 Online & Running
**Uptime:** {uptime}
**Version:** 2.0.0
**Features:** 8 Commands Available

**System Info:**
• Python Telegram Bot Library
• Enhanced Command Set
• Error Handling
• Professional Logging

**Commands Available:** 8
**Last Update:** {uptime}
    """
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle non-command messages intelligently."""
    user_message = update.message.text.lower()
    
    # Smart responses based on message content
    if any(word in user_message for word in ['hello', 'hi', 'hey']):
        response = "👋 Hello there! How can I help you today?"
    elif any(word in user_message for word in ['how are you', 'how r u']):
        response = "🤖 I'm doing great, thanks for asking! I'm ready to help with commands like /calc, /random, /joke, and more!"
    elif any(word in user_message for word in ['bye', 'goodbye', 'see you']):
        response = "👋 Goodbye! Feel free to come back anytime. Use /start to see what I can do!"
    elif any(word in user_message for word in ['thanks', 'thank you', 'thx']):
        response = "😊 You're welcome! I'm here to help. Try /help to see all my features!"
    elif any(word in user_message for word in ['what can you do', 'help me']):
        response = "🤖 I can do lots of things! Here are some highlights:\n\n• 🧮 Calculator: /calc 2+2\n• 🎲 Random numbers: /random 1-100\n• 😄 Jokes: /joke\n• 🕐 Time: /time\n\nUse /help for the full list!"
    elif '?' in user_message:
        response = "🤔 That's an interesting question! I can help with calculations, random numbers, jokes, and more. Try /help to see what I can do!"
    else:
        response = f"💬 You said: \"{update.message.text}\"\n\n💡 **Tip:** I can do much more than just echo messages! Try /help to see all my features."
    
    await update.message.reply_text(response)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("calc", calc_command))
    application.add_handler(CommandHandler("random", random_command))
    application.add_handler(CommandHandler("joke", joke_command))
    application.add_handler(CommandHandler("coin", coin_command))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("status", status))
    
    # Add message handler for non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("🤖 Starting Enhanced Telegram Bot...")
    print("📱 Bot is now running and listening for messages!")
    print("🔧 Available commands: /start, /help, /time, /calc, /random, /joke, /coin, /dice, /status")
    print("⏹️  Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
