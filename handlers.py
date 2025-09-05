from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import datetime, timedelta
from config import Config
from database import Database
from keyboards import *

config = Config()
db = Database()

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE, db, config):
    user = update.effective_user
    user_id = user.id
    
    # Foydalanuvchini bazaga qo'shish
    db.add_user(user_id, user.first_name, user.username)
    
    # Premium kanalga a'zoligini tekshirish
    is_member = await check_channel_membership(user_id, context, config)
    
    if is_member:
        end_date = db.get_subscription_end_date(user_id)
        await update.message.reply_text(
            f"Salom {user.first_name}! ✅ Siz allaqachon premium a'zosiz.\n"
            f"🗓 A'zolik muddati: {end_date}",
            reply_markup=get_admin_keyboard() if str(user_id) in config.ADMIN_IDS else None
        )
    else:
        await update.message.reply_text(
            f"Salom {user.first_name}! 👋\n\n"
            f"Bizning premium pulli kanalimizga a'zo bo'lish uchun quyidagi obuna turlaridan birini tanlang:",
            reply_markup=get_subscription_keyboard()
        )

async def handle_check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE, db):
    user_id = update.effective_user.id
    end_date = db.get_subscription_end_date(user_id)
    
    if end_date:
        await update.message.reply_text(f"✅ Sizning obunangiz {end_date} gacha amal qiladi")
    else:
        await update.message.reply_text("❌ Sizda faol obuna mavjud emas. /start buyrug'i orqali obuna sotib olishingiz mumkin")

async def handle_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    plan_type = query.data.replace("sub_", "")
    
    if plan_type not in config.SUBSCRIPTION_PRICES:
        await query.edit_message_text("❌ Noto'g'ri obuna turi tanlandi.")
        return
    
    amount = config.SUBSCRIPTION_PRICES[plan_type]
    
    payment_text = (
        f"💳 To'lov qilish uchun quyidagi ma'lumotlardan foydalaning:\n\n"
        f"🏦 Karta raqami: <code>{config.CARD_NUMBER}</code>\n"
        f"👤 Karta egasi: {config.CARDHOLDER_NAME}\n"
        f"💵 To'lov miqdori: {amount:,} so'm\n\n"
        f"📄 To'lovni amalga oshirgach, chekni (screenshot yoki PDF) shu yerga yuboring."
        f"✅ Admin tomonidan tekshirilgach, siz kanalga qo'shilasiz."
    )
    
    await query.edit_message_text(
        payment_text, 
        parse_mode='HTML',
        reply_markup=None
    )
    
    # Foydalanuvchini to'lov kutilayotgan holatga o'tkazish
    context.user_data['awaiting_payment'] = True
    context.user_data['selected_plan'] = plan_type

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_payment', False):
        return
    
    user_id = update.message.from_user.id
    plan_type = context.user_data['selected_plan']
    amount = config.SUBSCRIPTION_PRICES[plan_type]
    
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = 'photo'
    else:
        file_id = update.message.document.file_id
        file_type = 'document'
    
    # To'lovni ma'lumotlar bazasiga qo'shish
    payment_id = db.add_payment(user_id, amount, file_id, file_type)
    
    await update.message.reply_text(
        "✅ To'lov cheki qabul qilindi. Admin tomonidan tekshirilmoqda. Iltimos, kuting...",
        reply_markup=None
    )
    
    # Adminlarga xabar berish
    for admin_id in config.ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=int(admin_id),
                text=f"🆕 Yangi to'lov!\n\n👤 Foydalanuvchi: @{update.message.from_user.username}\n🆔 ID: {user_id}\n💵 Miqdor: {amount:,} so'm\n📦 Obuna: {plan_type}",
                reply_markup=get_payment_confirmation_keyboard(payment_id)
            )
            
            if file_type == 'photo':
                await context.bot.send_photo(
                    chat_id=int(admin_id),
                    photo=file_id,
                    caption="📄 To'lov cheki"
                )
            else:
                await context.bot.send_document(
                    chat_id=int(admin_id),
                    document=file_id,
                    caption="📄 To'lov cheki"
                )
        except Exception as e:
            print(f"Xatolik adminga xabar yuborishda: {e}")
    
    # Foydalanuvchi holatini tozalash
    context.user_data['awaiting_payment'] = False
    del context.user_data['selected_plan']

async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    admin_id = query.from_user.id
    
    if str(admin_id) not in config.ADMIN_IDS:
        await query.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if data.startswith('pay_approve_'):
        payment_id = int(data.replace('pay_approve_', ''))
        db.update_payment_status(payment_id, 'approved', admin_id)
        await query.message.reply_text("✅ To'lov tasdiqlandi!")
        
    elif data.startswith('pay_reject_'):
        payment_id = int(data.replace('pay_reject_', ''))
        db.update_payment_status(payment_id, 'rejected')
        await query.message.reply_text("❌ To'lov rad etildi!")

async def handle_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in config.ADMIN_IDS:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    total_users, premium_users = db.get_user_stats()
    
    stats_text = (
        f"📊 Bot statistikasi:\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"⭐ Premium a'zolar: {premium_users}\n"
        f"👤 Oddiy foydalanuvchilar: {total_users - premium_users}"
    )
    
    await update.message.reply_text(stats_text)

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in config.ADMIN_IDS:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if not context.args:
        await update.message.reply_text("📝 Xabarni yuborish uchun: /broadcast <xabar matni>")
        return
    
    message = " ".join(context.args)
    all_users = db.get_all_users()
    success_count = 0
    
    for user in all_users:
        try:
            await context.bot.send_message(chat_id=user, text=message)
            success_count += 1
        except Exception as e:
            print(f"Xatolik foydalanuvchiga xabar yuborishda: {e}")
    
    await update.message.reply_text(f"✅ Xabar {success_count}/{len(all_users)} foydalanuvchiga yuborildi.")

async def handle_add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in config.ADMIN_IDS:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("👤 Foydalanuvchi qo'shish uchun: /adduser <user_id> <obuna_turi>")
        return
    
    try:
        target_user_id = int(context.args[0])
        plan_type = context.args[1]
        
        if plan_type not in config.SUBSCRIPTION_DURATIONS:
            await update.message.reply_text("❌ Noto'g'ri obuna turi. Qabul qilinadigan turlar: 1_oy, 3_oy, 6_oy, 1_yil")
            return
        
        duration_days = config.SUBSCRIPTION_DURATIONS[plan_type]
        amount = config.SUBSCRIPTION_PRICES[plan_type]
        
        end_date = db.add_subscription(target_user_id, plan_type, amount, duration_days)
        
        await update.message.reply_text(
            f"✅ Foydalanuvchi {target_user_id} ga {plan_type} obunasi qo'shildi.\n"
            f"🗓 Obuna muddati: {end_date} gacha"
        )
        
    except ValueError:
        await update.message.reply_text("❌ User ID raqam bo'lishi kerak.")

async def handle_remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in config.ADMIN_IDS:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if not context.args:
        await update.message.reply_text("👤 Foydalanuvchini olib tashlash uchun: /removeuser <user_id>")
        return
    
    try:
        target_user_id = int(context.args[0])
        db.remove_subscription(target_user_id)
        
        await update.message.reply_text(f"✅ Foydalanuvchi {target_user_id} ning obunasi bekor qilindi.")
            
    except ValueError:
        await update.message.reply_text("❌ User ID raqam bo'lishi kerak.")

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if str(user_id) not in config.ADMIN_IDS:
        await query.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if data == "admin_stats":
        total_users, premium_users = db.get_user_stats()
        stats_text = f"📊 Statistika:\nJami: {total_users}\nPremium: {premium_users}"
        await query.message.reply_text(stats_text)
    
    elif data == "admin_payments":
        pending_payments = db.get_pending_payments()
        if pending_payments:
            text = "⏳ Kutilayotgan to'lovlar:\n\n"
            for payment in pending_payments:
                text += f"ID: {payment[0]}, Miqdor: {payment[2]} so'm\n"
            await query.message.reply_text(text)
        else:
            await query.message.reply_text("✅ Kutilayotgan to'lovlar yo'q")

async def check_channel_membership(user_id, context, config):
    try:
        member = await context.bot.get_chat_member(config.CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Kanal a'zoligini tekshirish xatosi: {e}")
        return False