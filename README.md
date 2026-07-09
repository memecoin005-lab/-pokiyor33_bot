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

## 🛠️ Deployment on Railway

### Step 1: Set Environment Variable

1. Go to your Railway project dashboard
2. Click on your deployed service
3. Go to the **Variables** tab
4. Add a new variable:
   - **Key:** `TELEGRAM_TOKEN`
   - **Value:** `your_bot_token_from_botfather`
5. Click **Deploy** to restart

### Step 2: Deploy from GitHub

1. Push your code to GitHub
2. On Railway, click **New Project**
3. Select **Deploy from GitHub repo**
4. Choose your repository
5. Wait for build and deployment

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
cp .env.example .env
# Edit .env and add your TELEGRAM_TOKEN

# Run the bot
python main.py
