import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from database import Database
from config import Config
from handlers import *

# Log konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(name)

# Database va Config
db = Database()
config = Config()

# Bot ilovasini yaratish
application = Application.builder().token(config.BOT_TOKEN).build()

# Handlers - BIR XIL! ✅
application.add_handler(CommandHandler("start", lambda u, c: handle_start(u, c, db, config)))
application.add_handler(CommandHandler("check", lambda u, c: handle_check_subscription(u, c, db)))
application.add_handler(CommandHandler("stats", handle_stats))
application.add_handler(CommandHandler("broadcast", handle_broadcast))
application.add_handler(CommandHandler("adduser", handle_add_user))
application.add_handler(CommandHandler("removeuser", handle_remove_user))

application.add_handler(CallbackQueryHandler(handle_subscription_callback, pattern="^sub_"))
application.add_handler(CallbackQueryHandler(handle_payment_callback, pattern="^pay_"))
application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^admin_"))

application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
application.add_handler(MessageHandler(filters.DOCUMENT, handle_receipt))

@app.route('/')
def home():
    return "🤖 Premium Telegram Bot - Webhook Mode ishlayapti!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Webhook ma'lumotlarini olish
        update_data = request.get_json()
        update = Update.de_json(update_data, application.bot)
        
        # Update ni qayta ishlash
        application.process_update(update)
        
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook xatosi: {e}")
        return "Error", 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        # Webhook URL ni o'rnatish
        webhook_url = f"https://{request.host}/webhook"
        success = application.bot.set_webhook(webhook_url)
        
        if success:
            return f"✅ Webhook o'rnatildi: {webhook_url}"
        else:
            return f"❌ Webhook o'rnatilmadi"
    except Exception as e:
        return f"❌ Webhook o'rnatishda xato: {e}"

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "telegram-bot-webhook"}

# Server ishga tushganda webhook ni o'rnatish
@app.before_first_request
def initialize():
    try:
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')}/webhook"
        if webhook_url and 'render.com' in webhook_url:
            application.bot.set_webhook(webhook_url)
            logger.info(f"Webhook o'rnatildi: {webhook_url}")
    except Exception as e:
        logger.error(f"Webhook o'rnatishda xato: {e}")

if name == 'main':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
