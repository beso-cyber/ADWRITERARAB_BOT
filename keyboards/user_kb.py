from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def user_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✨ إنشاء إعلان")],
            [KeyboardButton(text="📌 رصيدي"), KeyboardButton(text="💳 الاشتراك")],
        ],
        resize_keyboard=True,
    )
