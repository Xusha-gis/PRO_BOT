import os
from dotenv import load_dotenv

# .env fayldagi o'zgaruvchilarni yuklash
load_dotenv()

# Telegram Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin ID (ixtiyoriy)
ADMIN_IDS = os.getenv("ADMIN_IDS")

# Kanal ID (ixtiyoriy)
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Karta ma'lumotlari (ixtiyoriy)
CARD_NUMBER = os.getenv("CARD_NUMBER")
CARDHOLDER_NAME = os.getenv("CARDHOLDER_NAME")

# Render URL (Webhook uchun)
RENDER_URL = os.getenv("RENDER_URL", "https://pro-bot-o36t.onrender.com")
