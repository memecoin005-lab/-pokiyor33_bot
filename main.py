"""
@pokiyor33_bot - Multi-purpose Telegram Bot
FIXED: Environment variable loading issue
DEPLOY: Railway + GitHub
"""

import os
import sys
import re
import logging
import random
from typing import Dict, Any

# ===================== LOAD ENVIRONMENT VARIABLES FIRST =====================
# Try to load .env file if it exists (local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded (if exists)")
except ImportError:
    print("ℹ️ python-dotenv not installed, using system environment")

# Get token - THIS MUST COME AFTER load_dotenv()
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Check if token exists - if not, exit with clear message
if TELEGRAM_TOKEN is None:
    print("\n" + "="*70)
    print("❌ ERROR: TELEGRAM_TOKEN environment variable not found!")
    print("="*70)
    print("\n📌 TO FIX THIS ON RAILWAY:")
    print("  1. Go to your Railway project dashboard")
    print("  2. Click on your deployed service")
    print("  3. Click the 'Variables' tab")
    print("  4. Add a new variable:")
    print("     📝 Key:   TELEGRAM_TOKEN")
    print("     📝 Value: <your_bot_token_from_BotFather>")
    print("  5. Click 'Deploy' to restart\n")
    print("📌 TO FIX LOCALLY:")
    print("  1. Create a .env file in the project root")
    print("  2. Add: TELEGRAM_TOKEN=your_bot_token")
    print("  3. Run: python main.py\n")
    print("="*70)
    sys.exit(1)

# Now we have the token, proceed with imports that need it
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

logger.info("="*60)
logger.info(f"✅ TELEGRAM_TOKEN loaded successfully")
logger.info(f"🔑 Token starts with: {TELEGRAM_TOKEN[:10]}...")
logger.info(f"📏 Token length: {len(TELEGRAM_TOKEN)} characters")
logger.info("="*60)

# Conversation states
WAITING_FOR_URL = 1
WAITING_FOR_PROMPT = 2
WAITING_FOR_TEXT = 3

# ===================== UTILITY FUNCTIONS =====================

def is_valid_url(url: str) -> bool:
    """Check if the URL is valid"""
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
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
        encoded_prompt = requests.utils.quote(prompt)
        seed = random.randint(1, 1000000)
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
        f"*Select an option below:*"
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
        "`/help` - Show this message\n"
        "`/shorten` - Shorten a URL\n"
        "`/generate` - Generate AI image\n"
        "`/count` - Count words & characters\n"
        "`/airtime` - Airtime conversion info\n"
        "`/cancel` - Cancel current operation\n\n"
        "🤖 *Features:*\n"
        "• URL Shortener (spoo.me)\n"
        "• AI Image Generator (pollinations.ai)\n"
        "• Word & Character Counter\n"
        "• Airtime Conversion Info (Nigeria)"
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
        "*Example:* `https://www.example.com/very-long-url`\n\n"
        "*(Send /cancel to cancel)*",
        parse_mode='Markdown'
    )
    return WAITING_FOR_URL

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input for shortening"""
    url = update.message.text.strip()
    
    if url.lower() == '/cancel':
        await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    if not is_valid_url(url):
        await update.message.reply_text(
            "❌ *Invalid URL*\n\n"
            "Please send a valid URL starting with `http://` or `https://`",
            parse_mode='Markdown'
        )
        return WAITING_FOR_URL
    
    processing_msg = await update.message.reply_text("⏳ Shortening URL...")
    
    result = await shorten_url_api(url)
    
    if result and result.get('short_url'):
        short_url = result.get('short_url')
        stats = result.get('stats', {})
        clicks = stats.get('total', 0)
        
        response_message = (
            f"✅ *URL Shortened Successfully!*\n\n"
            f"🔗 *Original:*\n`{url}`\n\n"
            f"✂️ *Shortened:*\n`{short_url}`\n\n"
            f"📊 *Total Clicks:* {clicks}"
        )
        
        keyboard = [[
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
            "The service might be temporarily unavailable. Please try again.",
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
    
    if prompt.lower() == '/cancel':
        await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    if len(prompt) < 3:
        await update.message.reply_text(
            "❌ *Prompt too short*\n\n"
            "Please provide a more detailed description (at least 3 characters).",
            parse_mode='Markdown'
        )
        return WAITING_FOR_PROMPT
    
    processing_msg = await update.message.reply_text("🎨 Generating your image... This may take a few seconds.")
    
    image_url = await generate_image_api(prompt)
    
    if image_url:
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=(
                    f"🖼️ *AI Generated Image*\n\n"
                    f"📝 *Prompt:* {prompt}"
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
            "The service might be temporarily unavailable. Please try again.",
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
    
    if sentence_count == 0 and word_count > 0:
        sentence_count = 1
    
    result = (
        f"📊 *Text Analysis Results*\n\n"
        f"📝 *Words:* `{word_count}`\n"
        f"🔤 *Characters (with spaces):* `{char_with_spaces}`\n"
        f"🔠 *Characters (without spaces):* `{char_without_spaces}`\n"
        f"📄 *Sentences:* `{sentence_count}`"
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
        "• Fund mobile money wallets (MTN MoMo, Airtel SmartCash)\n\n"
        "📱 *RocketPay*\n"
        "• Airtime-to-cash conversion\n"
        "• Bill payments & money transfers\n"
        "• Gift card trading\n\n"
        "📱 *MinatPay*\n"
        "• Convert airtime to cash\n"
        "• Buy data bundles\n"
        "• Pay TV subscriptions & electricity bills\n\n"
        "⚠️ *Important Notes:*\n"
        "• These apps typically charge a convenience fee (5-15%)\n"
        "• Always verify current rates before transacting\n"
        "• Rates may vary by network provider"
    )
    
    keyboard = [[
        InlineKeyboardButton("💰 Check Current Rates", callback_data='check_rates')
    ]]
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

# ===================== MAIN FUNCTION =====================

def main():
    """Start the bot"""
    logger.info("="*60)
    logger.info("🚀 Starting @pokiyor33_bot...")
    logger.info("="*60)
    
    try:
        # Create the application
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
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
        logger.info("📱 Your bot is live: https://t.me/pokiyor33_bot")
        logger.info("="*60)
        
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        logger.error("="*60)
        logger.error("Common issues and solutions:")
        logger.error("1. Invalid token - Get a new one from @BotFather")
        logger.error("2. Network issues - Check your internet connection")
        logger.error("3. Missing dependencies - Run: pip install -r requirements.txt")
        logger.error("="*60)
        sys.exit(1)

if __name__ == '__main__':
    main()
