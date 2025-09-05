# app_webhook.py
import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

from database import Database
from config import Config
from handlers import *

# Log konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database va Config
db = Database()
config = Config()

# Bot ilovasini yaratish (Application - 20.x)
application = Application.builder().token(config.BOT_TOKEN).build()

# Handlers — async funksiyalar bilan ishlaydi (handlers.py ichidagi funksiyalar async deb yozilgani uchun)
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
    """
    Telegram bot webhook endpoint.
    POST kelgan update'ni Applicationning update_queue'iga quyiqatni qo'yamiz.
    """
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)

        # Put update into the application's queue thread-safely.
        # application.update_queue is an asyncio.Queue created by Application.
        try:
            application.update_queue.put_nowait(update)
        except Exception:
            # Fallback: if put_nowait fails (rare), schedule using asyncio on application's loop
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(application.update_queue.put_nowait, update)

        return "OK", 200
    except Exception as e:
        logger.exception("Webhook xatosi:")
        return "Error", 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """
    Qo'lda webhook o'rnatish uchun endpoint.
    Render dagi URLni ishlatish uchun RENDER_EXTERNAL_HOSTNAME yoki RENDER_URL ni environmentga qo'ying.
    """
    try:
        host = os.environ.get('RENDER_EXTERNAL_HOSTNAME') or os.environ.get('RENDER_URL')
        if not host:
            return "RENDER_EXTERNAL_HOSTNAME yoki RENDER_URL muhit o'zgaruvchisi aniqlanmagan", 400

        webhook_url = f"https://{host}/webhook"
        success = application.bot.set_webhook(webhook_url)
        if success:
            return f"✅ Webhook o'rnatildi: {webhook_url}"
        else:
            return "❌ Webhook o'rnatilmadi", 500
    except Exception as e:
        logger.exception("Webhook o'rnatishda xato:")
        return f"❌ Xato: {e}", 500

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "telegram-bot-webhook"}

# Start Application in background (initialize/start its internal asyncio tasks)
def _start_application_background():
    """
    Application ni background asyncio loopda ishga tushiramiz.
    Bu usul gunicorn/.wsgi ichida Flask app import qilingan zahotiyoq botning Application ixtiyoriy
    ichki queue va handlerlari aktiv bo'lishini ta'minlaydi.
    """
    async def _start():
        await application.initialize()
        await application.start()
        logger.info("Telegram Application started (background).")

    # Run start coroutine in a separate thread with its own event loop
    def _run_loop():
        asyncio.run(_start())

    import threading
    t = threading.Thread(target=_run_loop, daemon=True)
    t.start()

# Flask boshlanishida background applicationni ishga tushiramiz
# Gunicorn import paytida ham bu kod ishlaydi (module import), shuning uchun yozdim.
_start_application_background()

# NOTE: Gunicorn start qilingan zahoti Flask app import bo'ladi va background thread boshlanadi.
# Gunicorn yordamida ishga tushirishni tavsiya qilaman:
# render.yaml ichida: startCommand: gunicorn app_webhook:app --bind 0.0.0.0:$PORT
