from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 عدد المستخدمين")],
            [KeyboardButton(text="➕ إضافة رصيد"), KeyboardButton(text="➖ خصم رصيد")],
            [KeyboardButton(text="⭐ تفعيل اشتراك")],   # ← زر جديد
            [KeyboardButton(text="📢 رسالة جماعية")],
            [KeyboardButton(text="↩️ رجوع للقائمة الرئيسية")],
        ],
        resize_keyboard=True,
    )
