from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_subscription_keyboard():
    keyboard = [
        [InlineKeyboardButton("1 oy - 20,000 so'm", callback_data="sub_1_oy")],
        [InlineKeyboardButton("3 oy - 55,000 so'm", callback_data="sub_3_oy")],
        [InlineKeyboardButton("6 oy - 105,000 so'm", callback_data="sub_6_oy")],
        [InlineKeyboardButton("1 yil - 185,000 so'm", callback_data="sub_1_yil")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Xabarnoma yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton("💰 To'lovlarni tekshirish", callback_data="admin_payments")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_confirmation_keyboard(payment_id):
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"pay_approve_{payment_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"pay_reject_{payment_id}")
        ],
    ]
    return InlineKeyboardMarkup(keyboard)