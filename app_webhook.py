import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import Config
from handlers import (
    handle_start,
    handle_check_subscription,
    handle_subscription_callback,
    handle_receipt,
    handle_payment_callback,
    handle_stats,
    handle_broadcast,
    handle_add_user,
    handle_remove_user,
    handle_admin_callback
)
from database import Database

# Config va Database
config = Config()
db = Database()

# Flask ilovasi
app = Flask(__name__)

# Telegram bot Application (updater=None qo‘yildi!)
application = (
    Application.builder()
    .token(config.BOT_TOKEN)
    .updater(None)
    .build()
)

# Handlerlarni qo‘shish
application.add_handler(CommandHandler("start", lambda u, c: handle_start(u, c, db, config)))
application.add_handler(CommandHandler("check", lambda u, c: handle_check_subscription(u, c, db)))
application.add_handler(CommandHandler("stats", handle_stats))
application.add_handler(CommandHandler("broadcast", handle_broadcast))
application.add_handler(CommandHandler("adduser", handle_add_user))
application.add_handler(CommandHandler("removeuser", handle_remove_user))

application.add_handler(CallbackQueryHandler(handle_subscription_callback, pattern="^sub_"))
application.add_handler(CallbackQueryHandler(handle_payment_callback, pattern="^(pay_approve_|pay_reject_)"))
application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^(admin_stats|admin_payments)"))

# Foydalanuvchilar yuborgan to‘lov cheklari (foto + document)
application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
application.add_handler(MessageHandler(filters.ATTACHMENT & filters.Document.ALL, handle_receipt))

# Flask route – Telegram webhook uchun
@app.route(f"/{config.BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/")
def home():
    return "✅ Bot ishlayapti!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
