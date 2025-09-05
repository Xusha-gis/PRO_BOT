import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from database import Database
from config import Config
from handlers import *

# Log konfiguratsiyasi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PremiumBot:
    def __init__(self):
        self.db = Database()
        self.config = Config()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await handle_start(update, context, self.db, self.config)
    
    async def check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await handle_check_subscription(update, context, self.db)
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Xatolik: {context.error}")

def main():
    bot = PremiumBot()
    
    # Bot ilovasini yaratish
    application = Application.builder().token(bot.config.BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("check", bot.check_subscription))
    application.add_handler(CommandHandler("stats", handle_stats))
    application.add_handler(CommandHandler("broadcast", handle_broadcast))
    application.add_handler(CommandHandler("adduser", handle_add_user))
    application.add_handler(CommandHandler("removeuser", handle_remove_user))
    
    application.add_handler(CallbackQueryHandler(handle_subscription_callback, pattern="^sub_"))
    application.add_handler(CallbackQueryHandler(handle_payment_callback, pattern="^pay_"))
    application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^admin_"))
    
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
    application.add_handler(MessageHandler(filters.DOCUMENT, handle_receipt))
    
    application.add_error_handler(bot.error_handler)
    
    # Botni ishga tushirish
    print("Bot ishga tushdi ✅")
    application.run_polling()

if __name__ == "__main__":
    main()
