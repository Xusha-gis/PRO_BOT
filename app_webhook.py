import os
import config
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Flask app
app = Flask(__name__)

# Telegram application
application = Application.builder().token(config.BOT_TOKEN).build()

# Webhook URL
WEBHOOK_URL = f"https://pro-bot-o36t.onrender.com/{config.BOT_TOKEN}"


# ------------------ Handlers ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot ishlayapti va webhook ulandi!")


application.add_handler(CommandHandler("start", start))


# ------------------ Flask routes ------------------

@app.route(f"/{config.BOT_TOKEN}", methods=["POST"])
def webhook():
    """Telegram webhook endpoint"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"


@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✅"


# ------------------ Auto webhook setup ------------------

@app.before_first_request
def set_webhook():
    """Automatically set Telegram webhook when app starts"""
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/setWebhook"
    data = {"url": WEBHOOK_URL}
    try:
        r = requests.post(url, data=data)
        print("SetWebhook response:", r.json())
    except Exception as e:
        print("Failed to set webhook:", e)


# ------------------ Run locally ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
