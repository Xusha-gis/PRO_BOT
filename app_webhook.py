from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os

# BOT TOKEN ni .env yoki Render environment variables ichidan olish
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

# Application (python-telegram-bot)
application = Application.builder().token(BOT_TOKEN).build()

# /start komandasi
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Salom! Bot muvaffaqiyatli ishlamoqda 🚀")

application.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"

# Webhookni o‘rnatish uchun GET endpoint
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    success = application.bot.set_webhook(webhook_url)
    if success:
        return f"✅ Webhook o‘rnatildi: {webhook_url}"
    else:
        return "❌ Webhook o‘rnatishda xatolik"

if __name__ == "__main__":
    app.run(port=5000)
