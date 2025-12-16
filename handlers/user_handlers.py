from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import FREE_POSTS
from database import add_user, get_user, update_credits, is_subscriber
from keyboards.user_kb import user_menu
from services.ai_service import generate_ads, ai_ready

router = Router()


@router.message(CommandStart())
async def start(msg: Message):
    user_id = msg.from_user.id
    if not get_user(user_id):
        add_user(user_id, FREE_POSTS)

    await msg.answer(
        "مرحباً بك في <b>بوت كتابة الإعلانات الاحترافي</b> ✨\n\n"
        "اختر من القائمة بالأسفل 👇",
        reply_markup=user_menu(),
    )


@router.message(F.text == "📌 رصيدي")
async def credits(msg: Message):
    user = get_user(msg.from_user.id)
    if not user:
        add_user(msg.from_user.id, FREE_POSTS)
        user = get_user(msg.from_user.id)

    credits_val = user[1]
    sub = is_subscriber(msg.from_user.id)

    await msg.answer(
        f"📌 <b>رصيدك الحالي:</b> {credits_val} إعلان\n"
        f"💳 <b>الاشتراك الشهري:</b> {'✅ فعّال' if sub else '❌ غير فعّال'}"
    )


@router.message(F.text == "💳 الاشتراك")
async def subs_info(msg: Message):
    await msg.answer(
        "💳 <b>الاشتراك</b>\n\n"
        "• يمكنك تفعيل اشتراك شهري (30 يوماً)\n"
        "• أو شراء رصيد إضافي\n\n"
        "📩 للتفعيل/الدفع: تواصل مع الإدارة."
    )


@router.message(F.text == "✨ إنشاء إعلان")
async def ask_for_input(msg: Message):
    await msg.answer(
        "📝 أرسل الآن وصفاً مختصراً للمنتج والجمهور في رسالة واحدة.\n\n"
        "مثال:\n"
        "<code>عطر رجالي فاخر - رجال 25-40 يهتمون بالأناقة</code>"
    )


@router.message()
async def generate(msg: Message):
    # تجاهل رسائل الأزرار اللي تم التعامل معها فوق
    if msg.text in ["✨ إنشاء إعلان", "📌 رصيدي", "💳 الاشتراك"]:
        return

    user_id = msg.from_user.id
    user = get_user(user_id)
    if not user:
        add_user(user_id, FREE_POSTS)
        user = get_user(user_id)

    credits_val = user[1]
    sub = is_subscriber(user_id)

    if not sub and credits_val <= 0:
        await msg.answer("❌ رصيدك انتهى. اشترك أو اطلب إضافة رصيد.")
        return

    # خصم 1 فقط لو ليس مشتركاً
    if not sub:
        update_credits(user_id, credits_val - 1)

    await msg.answer("⏳ جاري توليد الإعلان...")

    text = generate_ads(msg.text) if ai_ready() else "⚠️ GROQ_API_KEY غير مضاف."
    await msg.answer("✨ <b>الإعلانات المقترحة:</b>\n\n" + text)
