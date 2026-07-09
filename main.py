"""
@pokiyor33_bot - Simple and Working Telegram Bot
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

# Get token
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    print("❌ TELEGRAM_TOKEN not set! Add it in Railway Variables.")
    sys.exit(1)

# States for conversation
WAITING_FOR_URL = 1
WAITING_FOR_PROMPT = 2
WAITING_FOR_TEXT = 3

# ===================== COMMANDS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    keyboard = [
        [InlineKeyboardButton("🔗 Shorten URL", callback_data='shorten')],
        [InlineKeyboardButton("🖼️ Generate Image", callback_data='generate')],
        [InlineKeyboardButton("📊 Word Counter", callback_data='count')],
        [InlineKeyboardButton("💰 Airtime Info", callback_data='airtime')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    
    await update.message.reply_text(
        "👋 Hello! I'm @pokiyor33_bot\n\n"
        "I can help you with:\n"
        "🔗 Shorten URLs\n"
        "🖼️ Generate AI images\n"
        "📊 Count words\n"
        "💰 Airtime conversion info\n\n"
        "Select an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "📚 Commands:\n"
        "/start - Main menu\n"
        "/shorten - Shorten a URL\n"
        "/generate - Generate an image\n"
        "/count - Count words\n"
        "/airtime - Airtime info\n"
        "/help - This message"
    )

# ===================== URL SHORTENER =====================

async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start URL shortening"""
    await update.message.reply_text(
        "🔗 Send me a URL to shorten.\n"
        "Example: https://www.google.com\n\n"
        "Send /cancel to cancel"
    )
    return WAITING_FOR_URL

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL shortening"""
    url = update.message.text.strip()
    
    if url.lower() == '/cancel':
        await update.message.reply_text("❌ Cancelled")
        return ConversationHandler.END
    
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ Please send a valid URL starting with http:// or https://")
        return WAITING_FOR_URL
    
    await update.message.reply_text("⏳ Shortening...")
    
    try:
        # Try is.gd (most reliable)
        response = requests.get(
            f'https://is.gd/create.php?format=simple&url={url}',
            timeout=10
        )
        
        if response.status_code == 200:
            short_url = response.text.strip()
            await update.message.reply_text(
                f"✅ Shortened!\n\n"
                f"Original: {url}\n"
                f"Short: {short_url}"
            )
        else:
            await update.message.reply_text("❌ Failed to shorten. Please try again.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error shortening URL. Please try again.")
    
    return ConversationHandler.END

# ===================== IMAGE GENERATOR =====================

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start image generation"""
    await update.message.reply_text(
        "🖼️ Describe the image you want.\n"
        "Example: sunset over mountains\n\n"
        "Send /cancel to cancel"
    )
    return WAITING_FOR_PROMPT

async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image generation"""
    prompt = update.message.text.strip()
    
    if prompt.lower() == '/cancel':
        await update.message.reply_text("❌ Cancelled")
        return ConversationHandler.END
    
    if len(prompt) < 3:
        await update.message.reply_text("❌ Please give a longer description (3+ characters)")
        return WAITING_FOR_PROMPT
    
    await update.message.reply_text("🎨 Generating image...")
    
    try:
        # Use pollinations.ai
        encoded = requests.utils.quote(prompt)
        seed = random.randint(1, 999999)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?seed={seed}"
        
        await update.message.reply_photo(
            photo=image_url,
            caption=f"🖼️ {prompt}"
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Failed to generate image. Please try again.")
    
    return ConversationHandler.END

# ===================== WORD COUNTER =====================

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start word counting"""
    await update.message.reply_text(
        "📊 Send me text to count.\n"
        "Example: Hello world this is a test\n\n"
        "Send /cancel to cancel"
    )
    return WAITING_FOR_TEXT

async def handle_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle word counting"""
    text = update.message.text.strip()
    
    if text.lower() == '/cancel':
        await update.message.reply_text("❌ Cancelled")
        return ConversationHandler.END
    
    if not text:
        await update.message.reply_text("❌ Please send some text")
        return WAITING_FOR_TEXT
    
    words = len(text.split())
    chars = len(text)
    chars_no_space = len(text.replace(' ', ''))
    sentences = text.count('.') + text.count('!') + text.count('?')
    
    await update.message.reply_text(
        f"📊 Results:\n\n"
        f"Words: {words}\n"
        f"Characters: {chars}\n"
        f"Characters (no spaces): {chars_no_space}\n"
        f"Sentences: {sentences}"
    )
    
    return ConversationHandler.END

# ===================== AIRTIME INFO =====================

async def airtime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Airtime conversion info"""
    await update.message.reply_text(
        "💰 Airtime to Cash Apps (Nigeria)\n\n"
        "1. Tingtel - Convert airtime to cash\n"
        "2. RocketPay - Airtime + bills\n"
        "3. MinatPay - Airtime + data\n\n"
        "⚠️ Fees: 5-15%\n"
        "Download from Play Store only"
    )

# ===================== CANCEL =====================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END

# ===================== BUTTON CALLBACK =====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'shorten':
        await shorten_command(query, context)
    elif data == 'generate':
        await generate_command(query, context)
    elif data == 'count':
        await count_command(query, context)
    elif data == 'airtime':
        await airtime_command(query, context)
    elif data == 'help':
        await help_command(query, context)

# ===================== ERROR HANDLER =====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    # Don't send error messages to users - just log it

# ===================== MAIN =====================

def main():
    """Start the bot"""
    logger.info("🚀 Starting bot...")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('airtime', airtime_command))
    app.add_handler(CommandHandler('cancel', cancel))
    
    # Conversation handlers
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('shorten', shorten_command)],
        states={WAITING_FOR_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('generate', generate_command)],
        states={WAITING_FOR_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('count', count_command)],
        states={WAITING_FOR_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_count)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running!")
    app.run_polling()

if __name__ == '__main__':
    main()
