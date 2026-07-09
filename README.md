# @pokiyor33_bot 🤖

A powerful multi-purpose Telegram bot with URL shortening, AI image generation, word counting, and more!

## ✨ Features

- 🔗 **URL Shortener** - Shorten long URLs instantly using spoo.me API
- 🖼️ **AI Image Generator** - Create images from text using pollinations.ai
- 📊 **Word Counter** - Count words, characters, sentences, paragraphs
- 💰 **Airtime Converter** - Information about airtime to cash conversion
- 📱 **Interactive UI** - Inline keyboards for easy navigation
- ⚡ **Fast & Reliable** - Optimized for performance

## 🚀 Commands

| Command | Description |
|---------|-------------|
| `/start` | Show main menu |
| `/help` | Show all commands |
| `/shorten` | Shorten a URL |
| `/generate` | Generate an AI image |
| `/count` | Count words and characters |
| `/airtime` | Airtime conversion info |
| `/cancel` | Cancel current operation |

## 🛠️ Deployment

### Prerequisites
- Python 3.9+
- Telegram Bot Token (from @BotFather)
- Railway account
- GitHub account

### Environment Variables
- `TELEGRAM_TOKEN`: Your bot token from @BotFather

### Deploy on Railway
1. Fork this repository on GitHub
2. Create a new project on Railway
3. Connect your GitHub repository
4. Add `TELEGRAM_TOKEN` as an environment variable
5. Deploy!

## 📦 Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/pokiyor33-bot.git
cd pokiyor33-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "TELEGRAM_TOKEN=your_bot_token" > .env

# Run the bot
python main.py
