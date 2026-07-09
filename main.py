"""
@pokiyor33_bot - Fully Working Telegram Bot
"""

import os
import sys
import logging
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler
)

# ===================== SETUP =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    print("❌ TELEGRAM_TOKEN not set!")
    sys.exit(1)

# Conversation states
WAITING_FOR_URL = 1
WAITING_FOR_PROMPT = 2
WAITING_FOR_TEXT = 3

# ===================== COMMANDS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - shows main menu"""
    keyboard = [
        [InlineKeyboardButton("🔗 Shorten URL", callback_data='shorten')],
        [InlineKeyboardButton("🖼️ Generate Image", callback_data='generate')],
        [InlineKeyboardButton("📊 Word Counter", callback_data='count')],
        [InlineKeyboardButton("💰 Airtime Info", callback_data='airtime')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    
    await update.message.reply_text(
        "👋 *Welcome to @pokiyor33_bot!*\n\n"
        "I can help you with:\n"
        "🔗 Shorten long URLs\n"
        "🖼️ Generate AI images\n"
        "📊 Count words & characters\n"
        "💰 Airtime conversion info\n\n"
        "*Select an option below:*",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "📚 *Available Commands:*\n\n"
        "/start - Show main menu\n"
        "/shorten - Shorten a URL\n"
        "/generate - Generate an image\n"
        "/count - Count words\n"
        "/airtime - Airtime info\n"
        "/help - This message\n\n"
        "*How to use:*\n"
        "1. Click a button or type a command\n"
        "2. Follow the instructions\n"
        "3. Get your result!",
        parse_mode='Markdown'
    )

# ===================== URL SHORTENER =====================

async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start URL shortening conversation"""
    # Handle both command and callback
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text(
            "🔗 *Send me a URL to shorten.*\n"
            "Example: `https://www.google.com`\n\n"
            "Send /cancel to cancel",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "🔗 *Send me a URL to shorten.*\n"
            "Example: `https://www.google.com`\n\n"
            "Send /cancel to cancel",
            parse_mode='Markdown'
        )
    return WAITING_FOR_URL

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL shortening"""
    url = update.message.text.strip()
    
    if url.lower() == '/cancel':
        await update.message.reply_text("❌ Cancelled. Type /start to begin again.")
        return ConversationHandler.END
    
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text(
            "❌ *Invalid URL*\n\n"
            "Please send a valid URL starting with `http://` or `https://`\n"
            "Example: `https://www.google.com`",
            parse_mode='Markdown'
        )
        return WAITING_FOR_URL
    
    # Send processing message
    msg = await update.message.reply_text("⏳ Shortening URL...")
    
    try:
        # Try is.gd API (most reliable)
        response = requests.get(
            f'https://is.gd/create.php?format=simple&url={url}',
            timeout=10
        )
        
        if response.status_code == 200:
            short_url = response.text.strip()
            await msg.delete()
            await update.message.reply_text(
                f"✅ *URL Shortened Successfully!*\n\n"
                f"🔗 *Original:*\n`{url}`\n\n"
                f"✂️ *Shortened:*\n`{short_url}`\n\n"
                f"Type /start to go back to menu.",
                parse_mode='Markdown'
            )
        else:
            await msg.delete()
            await update.message.reply_text(
                "❌ *Failed to shorten URL*\n\n"
                "Please try again later.\n"
                "Type /start to go back.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"URL shortening error: {e}")
        await msg.delete()
        await update.message.reply_text(
            "❌ *Error shortening URL*\n\n"
            "Please try again later.\n"
            "Type /start to go back.",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

# ===================== IMAGE GENERATOR =====================

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start image generation conversation"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text(
            "🖼️ *Describe the image you want.*\n"
            "Example: `sunset over mountains`\n\n"
            "Send /cancel to cancel",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "🖼️ *Describe the image you want.*\n"
            "Example: `sunset over mountains`\n\n"
            "Send /cancel to cancel",
            parse_mode='Markdown'
        )
    return WAITING_FOR_PROMPT

async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image generation"""
    prompt = update.message.text.strip()
    
    if prompt.lower() == '/cancel':
        await update.message.reply_text("❌ Cancelled. Type /start to begin again.")
        return ConversationHandler.END
    
    if len(prompt) < 3:
        await update.message.reply_text(
            "❌ *Prompt too short*\n\n"
            "Please provide a longer description (at least 3 characters).\n"
            "Example: `sunset over mountains`",
            parse_mode='Markdown'
        )
        return WAITING_FOR_PROMPT
    
    # Send processing message
    msg = await update.message.reply_text("🎨 Generating image... This may take a few seconds.")
    
    try:
        # Use pollinations.ai
        encoded = requests.utils.quote(prompt)
        seed = random.randint(1, 999999)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=768&seed={seed}&nologo=true"
        
        await msg.delete()
        await update.message.reply_photo(
            photo=image_url,
            caption=f"🖼️ *Generated Image*\n\n📝 *Prompt:* {prompt}\n\nType /start to go back.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        await msg.delete()
        await update.message.reply_text(
            "❌ *Failed to generate image*\n\n"
            "Please try again later.\n"
            "Type /start to go back.",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

# ===================== WORD COUNTER =====================

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start word counting conversation"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text(
            "📊 *Send me text to count.*\n"
            "Example: `Hello world this is a test`\n\n"
            "Send /cancel to cancel",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "📊 *Send me text to count.*\n"
            "Example: `Hello world this is a test`\n\n"
            "Send /cancel to cancel",
            parse_mode='Markdown'
        )
    return WAITING_FOR_TEXT

async def handle_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle word counting"""
    text = update.message.text.strip()
    
    if text.lower() == '/cancel':
        await update.message.reply_text("❌ Cancelled. Type /start to begin again.")
        return ConversationHandler.END
    
    if not text:
        await update.message.reply_text(
            "❌ *No text provided*\n\n"
            "Please send me some text to analyze.\n"
            "Example: `Hello world this is a test`",
            parse_mode='Markdown'
        )
        return WAITING_FOR_TEXT
    
    # Count everything
    words = len(text.split())
    chars = len(text)
    chars_no_space = len(text.replace(' ', '').replace('\n', ''))
    sentences = text.count('.') + text.count('!') + text.count('?')
    
    if sentences == 0 and words > 0:
        sentences = 1
    
    await update.message.reply_text(
        f"📊 *Text Analysis Results*\n\n"
        f"📝 *Words:* `{words}`\n"
        f"🔤 *Characters (with spaces):* `{chars}`\n"
        f"🔠 *Characters (without spaces):* `{chars_no_space}`\n"
        f"📄 *Sentences:* `{sentences}`\n\n"
        f"Type /start to go back.",
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END

# ===================== AIRTIME INFO =====================

async def airtime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Airtime conversion info"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text(
            "💰 *Airtime to Cash Apps (Nigeria)*\n\n"
            "📱 *Tingtel App*\n"
            "• Convert airtime to cash\n"
            "• Pay bills\n"
            "• Fund mobile money\n\n"
            "📱 *RocketPay*\n"
            "• Airtime to cash\n"
            "• Bill payments\n"
            "• Gift card trading\n\n"
            "📱 *MinatPay*\n"
            "• Airtime to cash\n"
            "• Buy data\n"
            "• Pay TV subscriptions\n\n"
            "⚠️ *Fees:* 5-15% convenience fee\n"
            "📱 *Download from Play Store only*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "💰 *Airtime to Cash Apps (Nigeria)*\n\n"
            "📱 *Tingtel App*\n"
            "• Convert airtime to cash\n"
            "• Pay bills\n"
            "• Fund mobile money\n\n"
            "📱 *RocketPay*\n"
            "• Airtime to cash\n"
            "• Bill payments\n"
            "• Gift card trading\n\n"
            "📱 *MinatPay*\n"
            "• Airtime to cash\n"
            "• Buy data\n"
            "• Pay TV subscriptions\n\n"
            "⚠️ *Fees:* 5-15% convenience fee\n"
            "📱 *Download from Play Store only*",
            parse_mode='Markdown'
        )

# ===================== CANCEL =====================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        "❌ *Cancelled*\n\n"
        "Type /start to begin again.",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

# ===================== BUTTON CALLBACK =====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    context.user_data['callback'] = True
    
    if data == 'shorten':
        await shorten_command(update, context)
    elif data == 'generate':
        await generate_command(update, context)
    elif data == 'count':
        await count_command(update, context)
    elif data == 'airtime':
        await airtime_command(update, context)
    elif data == 'help':
        await help_command(update, context)

# ===================== FALLBACK =====================

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any other messages"""
    await update.message.reply_text(
        "❓ *I don't understand that.*\n\n"
        "Type /start to see the main menu.",
        parse_mode='Markdown'
    )

# ===================== ERROR HANDLER =====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors silently"""
    logger.error(f"Error: {context.error}")
    # Don't send to user to avoid confusion

# ===================== MAIN =====================

def main():
    """Start the bot"""
    logger.info("🚀 Starting @pokiyor33_bot...")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('airtime', airtime_command))
    app.add_handler(CommandHandler('cancel', cancel))
    
    # Conversation handlers
    app.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('shorten', shorten_command),
            CallbackQueryHandler(shorten_command, pattern='^shorten$')
        ],
        states={
            WAITING_FOR_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('generate', generate_command),
            CallbackQueryHandler(generate_command, pattern='^generate$')
        ],
        states={
            WAITING_FOR_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('count', count_command),
            CallbackQueryHandler(count_command, pattern='^count$')
        ],
        states={
            WAITING_FOR_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_count)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    
    # Callback handler for other buttons
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Fallback for unknown messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running!")
    app.run_polling()

if __name__ == '__main__':
    main()
