"""
@pokiyor33_bot - Multi-purpose Telegram Bot
Deployed on Railway with GitHub integration
FIXED: Environment variable handling
"""

import os
import sys
import re
import logging
import random
from typing import Dict, Any

# Load environment variables from .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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

# ===================== LOGGING SETUP =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== CONFIGURATION =====================

# Try multiple ways to get the token
TOKEN = None

# Method 1: Direct from environment (Railway, Heroku, etc.)
TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Method 2: From .env file (local development)
if not TOKEN:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        TOKEN = os.environ.get('TELEGRAM_TOKEN')
        if TOKEN:
            logger.info("✅ Token loaded from .env file")
    except:
        pass

# Method 3: Hardcoded fallback (ONLY FOR TESTING - REMOVE IN PRODUCTION)
# WARNING: Never hardcode tokens in production!
if not TOKEN:
    # This is for demonstration only - replace with your actual token for testing
    # TOKEN = "YOUR_BOT_TOKEN_HERE"
    pass

# Check if token is set
if not TOKEN:
    logger.error("=" * 60)
    logger.error("❌ TELEGRAM_TOKEN environment variable not set!")
    logger.error("=" * 60)
    logger.error("")
    logger.error("To fix this issue:")
    logger.error("")
    logger.error("Option 1: Set on Railway (Recommended)")
    logger.error("  1. Go to your Railway project dashboard")
    logger.error("  2. Click on your deployed service")
    logger.error("  3. Go to the 'Variables' tab")
    logger.error("  4. Add a new variable:")
    logger.error("     Key:   TELEGRAM_TOKEN")
    logger.error("     Value: YOUR_BOT_TOKEN_FROM_BOTFATHER")
    logger.error("  5. Click 'Deploy' to restart")
    logger.error("")
    logger.error("Option 2: Set in .env file (Local Development)")
    logger.error("  1. Create a .env file in the project root")
    logger.error("  2. Add: TELEGRAM_TOKEN=your_bot_token")
    logger.error("  3. Run: python main.py")
    logger.error("")
    logger.error("Option 3: Set as environment variable")
    logger.error("  export TELEGRAM_TOKEN='your_bot_token'")
    logger.error("")
    logger.error("=" * 60)
    sys.exit(1)

logger.info(f"✅ Bot token loaded successfully")
logger.info(f"🔑 Token starts with: {TOKEN[:10]}...")
logger.info(f"📏 Token length: {len(TOKEN)} characters")

# Conversation states
WAITING_FOR_URL = 1
WAITING_FOR_PROMPT = 2
WAITING_FOR_TEXT = 3

# ===================== UTILITY FUNCTIONS =====================

def is_valid_url(url: str) -> bool:
    """Check if the URL is valid"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return re.match(url_pattern, url) is not None

async def shorten_url_api(url: str) -> Dict[str, Any]:
    """Shorten URL using spoo.me API"""
    try:
        response = requests.post(
            'https://spoo.me/',
            data={'url': url},
            headers={'Accept': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"URL shortening error: {e}")
        return None

async def generate_image_api(prompt: str) -> str:
    """Generate image using pollinations.ai API"""
    try:
        # Format the prompt for URL
        encoded_prompt = requests.utils.quote(prompt)
        seed = random.randint(1, 1000000)
        
        # Generate image URL
        image_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width=1024&height=768"
            f"&seed={seed}"
            f"&nologo=true"
            f"&nofeed=true"
        )
        return image_url
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None

# ===================== COMMAND HANDLERS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    first_name = user.first_name or "there"
    
    welcome_message = (
        f"👋 *Hello {first_name}!*\n\n"
        f"Welcome to *@pokiyor33_bot* - your all-in-one utility bot! 🚀\n\n"
        f"*Here's what I can do for you:*\n"
        f"🔗 `/shorten` - Shorten long URLs instantly\n"
        f"🖼️ `/generate` - Create AI images from text\n"
        f"📊 `/count` - Count words and characters\n"
        f"💰 `/airtime` - Airtime to cash conversion info\n"
        f"❓ `/help` - Show all available commands\n\n"
        f"*Select an option below or type a command:*"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔗 Shorten URL", callback_data='shorten')],
        [InlineKeyboardButton("🖼️ Generate Image", callback_data='generate')],
        [InlineKeyboardButton("📊 Word Counter", callback_data='count')],
        [InlineKeyboardButton("💰 Airtime Converter", callback_data='airtime')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📚 *Available Commands*\n\n"
        "`/start` - Show main menu\n"
        "`/shorten` - Shorten a URL\n"
        "`/generate` - Generate AI image\n"
        "`/count` - Count words & characters\n"
        "`/airtime` - Airtime conversion info\n"
        "`/help` - Show this message\n\n"
        "🤖 *Features Explained*\n"
        "• *URL Shortener* - Uses spoo.me API (free, no registration)\n"
        "• *AI Image Generator* - Uses pollinations.ai (free, unlimited)\n"
        "• *Word Counter* - Counts words, characters, sentences\n"
        "• *Airtime Info* - Reliable conversion apps for Nigeria\n\n"
        "📌 *How to use*\n"
        "1. Type a command (e.g., /shorten)\n"
        "2. Follow the instructions\n"
        "3. Get your result instantly!\n\n"
        "💡 *Tip:* You can also click the buttons below to start!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔗 Shorten URL", callback_data='shorten')],
        [InlineKeyboardButton("🖼️ Generate Image", callback_data='generate')],
        [InlineKeyboardButton("📊 Word Counter", callback_data='count')],
        [InlineKeyboardButton("💰 Airtime Info", callback_data='airtime')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# ===================== URL SHORTENER =====================

async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /shorten command"""
    await update.message.reply_text(
        "🔗 *URL Shortener*\n\n"
        "Please send me the URL you want to shorten.\n\n"
        "*Example:* `https://www.example.com/very-long-url-with-many-parameters`\n\n"
        "*(Send /cancel to cancel)*",
        parse_mode='Markdown'
    )
    return WAITING_FOR_URL

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input for shortening"""
    url = update.message.text.strip()
    
    # Check if user wants to cancel
    if url.lower() == '/cancel':
        await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    # Validate URL
    if not is_valid_url(url):
        await update.message.reply_text(
            "❌ *Invalid URL*\n\n"
            "Please send a valid URL starting with `http://` or `https://`\n"
            "Example: `https://www.google.com`",
            parse_mode='Markdown'
        )
        return WAITING_FOR_URL
    
    # Show processing message
    processing_msg = await update.message.reply_text("⏳ Shortening URL...")
    
    # Call the API
    result = await shorten_url_api(url)
    
    if result and result.get('short_url'):
        short_url = result.get('short_url')
        stats = result.get('stats', {})
        clicks = stats.get('total', 0)
        
        response_message = (
            f"✅ *URL Shortened Successfully!*\n\n"
            f"🔗 *Original:*\n`{url}`\n\n"
            f"✂️ *Shortened:*\n`{short_url}`\n\n"
            f"📊 *Stats:* {clicks} total clicks"
        )
        
        # Add a button to copy the link
        keyboard = [[
            InlineKeyboardButton("📋 Copy Link", callback_data=f'copy_{short_url}'),
            InlineKeyboardButton("🔗 Open Link", url=short_url)
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_msg.delete()
        await update.message.reply_text(
            response_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await processing_msg.delete()
        await update.message.reply_text(
            "❌ *Failed to shorten URL*\n\n"
            "The service might be temporarily unavailable.\n"
            "Please try again in a few minutes.",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

# ===================== IMAGE GENERATOR =====================

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generate command"""
    await update.message.reply_text(
        "🖼️ *AI Image Generator*\n\n"
        "Describe the image you want me to create.\n\n"
        "*Example prompts:*\n"
        "• `A beautiful sunset over a mountain lake`\n"
        "• `A futuristic city with flying cars at night`\n"
        "• `A cute cat wearing a wizard hat`\n\n"
        "*(Send /cancel to cancel)*",
        parse_mode='Markdown'
    )
    return WAITING_FOR_PROMPT

async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image generation prompt"""
    prompt = update.message.text.strip()
    
    # Check if user wants to cancel
    if prompt.lower() == '/cancel':
        await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    # Validate prompt
    if len(prompt) < 3:
        await update.message.reply_text(
            "❌ *Prompt too short*\n\n"
            "Please provide a more detailed description (at least 3 characters).",
            parse_mode='Markdown'
        )
        return WAITING_FOR_PROMPT
    
    # Show processing message
    processing_msg = await update.message.reply_text("🎨 Generating your image... This may take a few seconds.")
    
    # Generate image
    image_url = await generate_image_api(prompt)
    
    if image_url:
        try:
            # Send the generated image
            await update.message.reply_photo(
                photo=image_url,
                caption=(
                    f"🖼️ *AI Generated Image*\n\n"
                    f"📝 *Prompt:* {prompt}\n\n"
                    f"⚡ *Note:* Images are generated using AI and may not be perfect."
                ),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending image: {e}")
            await update.message.reply_text(
                f"❌ *Error sending image*\n\n"
                f"Here's the generated image URL:\n`{image_url}`\n\n"
                f"You can open this link in your browser.",
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(
            "❌ *Failed to generate image*\n\n"
            "The service might be temporarily unavailable.\n"
            "Please try again in a few minutes.",
            parse_mode='Markdown'
        )
    
    await processing_msg.delete()
    return ConversationHandler.END

# ===================== WORD COUNTER =====================

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /count command"""
    await update.message.reply_text(
        "📊 *Word & Character Counter*\n\n"
        "Send me any text and I'll analyze it.\n\n"
        "*Example:* `This is a sample text to count words and characters.`\n\n"
        "*(Send /cancel to cancel)*",
        parse_mode='Markdown'
    )
    return WAITING_FOR_TEXT

async def handle_count_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text for counting"""
    text = update.message.text.strip()
    
    # Check if user wants to cancel
    if text.lower() == '/cancel':
        await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    if not text:
        await update.message.reply_text(
            "❌ *No text provided*\n\n"
            "Please send me some text to analyze.",
            parse_mode='Markdown'
        )
        return WAITING_FOR_TEXT
    
    # Count everything
    word_count = len(text.split())
    char_with_spaces = len(text)
    char_without_spaces = len(text.replace(' ', '').replace('\n', ''))
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    
    # If no sentence ending punctuation, count as 1 sentence
    if sentence_count == 0 and word_count > 0:
        sentence_count = 1
    
    # Count paragraphs
    paragraphs = [p for p in text.split('\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Average word length
    avg_word_length = char_without_spaces / word_count if word_count > 0 else 0
    
    # Reading time (approx 200 words per minute)
    reading_time = round(word_count / 200, 1)
    
    result = (
        f"📊 *Text Analysis Results*\n\n"
        f"📝 *Words:* `{word_count}`\n"
        f"🔤 *Characters (with spaces):* `{char_with_spaces}`\n"
        f"🔠 *Characters (without spaces):* `{char_without_spaces}`\n"
        f"📄 *Sentences:* `{sentence_count}`\n"
        f"📃 *Paragraphs:* `{paragraph_count}`\n"
        f"📏 *Avg word length:* `{avg_word_length:.1f}` characters\n"
        f"⏱️ *Reading time:* `{reading_time}` minute(s)\n\n"
        f"💡 *Tip:* Longer texts are analyzed more accurately!"
    )
    
    await update.message.reply_text(result, parse_mode='Markdown')
    return ConversationHandler.END

# ===================== AIRTIME CONVERTER =====================

async def airtime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /airtime command"""
    info = (
        "💰 *Airtime to Cash Conversion*\n\n"
        "Here are some reliable apps for converting airtime to cash in Nigeria:\n\n"
        "📱 *Tingtel App*\n"
        "• Fast airtime to cash conversion\n"
        "• Pay utility bills\n"
        "• Fund mobile money wallets (MTN MoMo, Airtel SmartCash)\n"
        "• Available on Play Store and App Store\n\n"
        "📱 *RocketPay*\n"
        "• Airtime-to-cash conversion\n"
        "• Bill payments & money transfers\n"
        "• Gift card trading\n"
        "• Available on Play Store\n\n"
        "📱 *MinatPay*\n"
        "• Convert airtime to cash\n"
        "• Buy data bundles\n"
        "• Pay TV subscriptions & electricity bills\n\n"
        "⚠️ *Important Notes:*\n"
        "• These apps typically charge a convenience fee (5-15%)\n"
        "• Always verify current rates before transacting\n"
        "• Rates may vary by network provider\n"
        "• Only use official app stores to download"
    )
    
    keyboard = [
        [InlineKeyboardButton("📱 Download Tingtel", url="https://play.google.com/store/apps/details?id=com.tingtel")],
        [InlineKeyboardButton("📱 Download RocketPay", url="https://play.google.com/store/apps/details?id=com.rocketpay")],
        [InlineKeyboardButton("💰 Check Current Rates", callback_data='check_rates')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        info,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# ===================== CANCEL COMMAND =====================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any ongoing conversation"""
    await update.message.reply_text(
        "❌ *Operation Cancelled*\n\n"
        "You can start over with /start",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

# ===================== CALLBACK QUERY HANDLER =====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
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
    elif data == 'check_rates':
        await query.message.reply_text(
            "💰 *Current Airtime Rates (Approximate)*\n\n"
            "• MTN: 70-75% of value\n"
            "• Airtel: 75-80% of value\n"
            "• Glo: 70-75% of value\n"
            "• 9mobile: 75-80% of value\n\n"
            "⚠️ *Note:* Rates change daily. Check the apps for current rates.",
            parse_mode='Markdown'
        )
    elif data.startswith('copy_'):
        # Handle copy link button
        short_url = data.replace('copy_', '')
        await query.message.reply_text(
            f"📋 *Copy this link:*\n`{short_url}`\n\n"
            "You can copy it manually from this message.",
            parse_mode='Markdown'
        )

# ===================== UNKNOWN COMMAND HANDLER =====================

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "❓ *Unknown Command*\n\n"
        "Type `/help` to see available commands\n"
        "or `/start` to see the main menu.",
        parse_mode='Markdown'
    )

# ===================== ERROR HANDLER =====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ *An error occurred*\n\n"
            "Please try again later or contact support.\n"
            "Error has been logged.",
            parse_mode='Markdown'
        )

# ===================== HEALTH CHECK ENDPOINT =====================

# This is for Railway's health checks
async def health_check():
    """Simple health check function"""
    return {"status": "healthy", "timestamp": "2026-07-09"}

# ===================== MAIN FUNCTION =====================

def main():
    """Start the bot"""
    logger.info("=" * 60)
    logger.info("🚀 Starting @pokiyor33_bot...")
    logger.info("=" * 60)
    logger.info(f"✅ Bot token loaded: {TOKEN[:10]}...{TOKEN[-5:]}")
    logger.info(f"📱 Bot username: @pokiyor33_bot")
    logger.info("=" * 60)
    
    try:
        # Create the application
        app = ApplicationBuilder().token(TOKEN).build()
        logger.info("✅ Application created successfully")
        
        # ===== CONVERSATION HANDLERS =====
        
        # URL shortening conversation
        url_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('shorten', shorten_command)],
            states={
                WAITING_FOR_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        
        # Image generation conversation
        image_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('generate', generate_command)],
            states={
                WAITING_FOR_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        
        # Word counter conversation
        count_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('count', count_command)],
            states={
                WAITING_FOR_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_count_text)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        
        # ===== ADD HANDLERS =====
        
        # Command handlers
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('help', help_command))
        app.add_handler(CommandHandler('airtime', airtime_command))
        app.add_handler(CommandHandler('cancel', cancel))
        
        # Conversation handlers
        app.add_handler(url_conv_handler)
        app.add_handler(image_conv_handler)
        app.add_handler(count_conv_handler)
        
        # Callback query handler
        app.add_handler(CallbackQueryHandler(button_callback))
        
        # Unknown command handler
        app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        
        # Error handler
        app.add_error_handler(error_handler)
        
        # ===== START THE BOT =====
        logger.info("✅ Bot is running! Listening for updates...")
        logger.info("=" * 60)
        logger.info("📱 Your bot is live: https://t.me/pokiyor33_bot")
        logger.info("=" * 60)
        
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        logger.error("=" * 60)
        logger.error("Common issues and solutions:")
        logger.error("1. Invalid token - Get a new one from @BotFather")
        logger.error("2. Network issues - Check your internet connection")
        logger.error("3. Missing dependencies - Run: pip install -r requirements.txt")
        logger.error("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
