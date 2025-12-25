from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from config import FREE_POSTS
from database import add_user, get_user, update_credits, is_subscriber
from keyboards.user_kb import user_menu
from services.ai_service import generate_ads, ai_ready

router = Router()

# =========================
# إعدادات الاشتراك (عدّل الرقم فقط)
# =========================
WHATSAPP_NUMBER = "962790846237"  # ← غيّر هذا الرقم فقط (بدون +)
WHATSAPP_TEXT = "مرحبا، أريد الاشتراك في كاتب إعلانات فاير."

def subscription_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 اشترك الآن", callback_data="sub_now")],
            [
                InlineKeyboardButton(
                    text="📲 تواصل واتساب",
                    url=f"https://wa.me/{WHATSAPP_NUMBER}?text={WHATSAPP_TEXT.replace(' ', '%20')}",
                )
            ],
        ]
    )


# =========================
# /start
# =========================
@router.message(CommandStart())
async def start(msg: Message):
    user_id = msg.from_user.id

    if not get_user(user_id):
        add_user(user_id, FREE_POSTS)

    await msg.answer(
        "👋 أهلاً بك في <b>كاتب إعلانات فاير</b> 🔥\n\n"
        "✍️ أكتب لك إعلان جاهز للنشر خلال ثوانٍ، بدون تعب أو خبرة.\n\n"
        "🎯 مناسب لـ:\n"
        "• متاجر أونلاين\n"
        "• خدمات (مطاعم، عيادات، صالونات، شركات)\n"
        "• مسوقين وإعلانات ممولة\n\n"
        "🎁 لديك تجربة مجانية للبدء الآن.\n\n"
        "👇 اختر من القائمة وابدأ",
        reply_markup=user_menu(),
        parse_mode="HTML",
    )


# =========================
# عرض الرصيد
# =========================
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
        f"💳 <b>الاشتراك الشهري:</b> {'✅ فعّال' if sub else '❌ غير فعّال'}",
        parse_mode="HTML",
    )


# =========================
# الاشتراك (زر + كتابة)
# =========================
@router.message((F.text == "💳 الاشتراك") | (F.text.strip().lower() == "اشتراك"))
async def subscription_entry(msg: Message):
    await msg.answer(
        "💳 <b>طرق الاشتراك في كاتب إعلانات فاير</b>\n\n"
        "اختر الباقة المناسبة لك:\n"
        "• 30 إعلان = <b>5$</b>\n"
        "• اشتراك شهري غير محدود = <b>8$</b>\n\n"
        "👇 اختر الطريقة المناسبة:",
        parse_mode="HTML",
        reply_markup=subscription_kb(),
    )


# =========================
# زر (اشترك الآن)
# =========================
@router.callback_query(F.data == "sub_now")
async def subscription_instructions(cb: CallbackQuery):
    await cb.message.answer(
        "💳 <b>خطوات تفعيل الاشتراك</b>\n\n"
        "1️⃣ اختر الباقة:\n"
        "• 30 إعلان = <b>5$</b>\n"
        "• اشتراك شهري غير محدود = <b>8$</b>\n\n"
        "2️⃣ حوّل المبلغ عبر:\n"
        "• زين كاش / Orange Money / تحويل محلي\n\n"
        "3️⃣ أرسل صورة التحويل هنا داخل البوت.\n\n"
        "⚡ سيتم تفعيل الاشتراك خلال دقائق.",
        parse_mode="HTML"
    )

    await cb.answer("تم إرسال خطوات التفعيل ✅", show_alert=True)





# =========================
# زر إنشاء إعلان
# =========================
@router.message(F.text == "✨ إنشاء إعلان")
async def ask_for_input(msg: Message):
    await msg.answer(
        "تمام 👍 خلّينا نكتب إعلان قوي.\n\n"
        "✍️ أرسل لي الآن *وصف المنتج أو الخدمة* بسطرين كحد أقصى.\n"
        "لا تقلق عن الصياغة، فقط الفكرة.\n\n"
        "📌 مثال:\n"
        "<code>عطر رجالي فاخر، ثبات عالي، مناسب للمناسبات – رجال 25-40</code>\n\n"
        "بعدها سأجهز لك الإعلان فورًا 🔥",
        parse_mode="HTML",
    )


# =========================
# Handler عام (توليد الإعلان)
# ⚠️ يجب أن يكون آخر شيء في الملف
# =========================
@router.message()
async def generate(msg: Message):
    # منع الاشتراك من الدخول هنا
    if msg.text and msg.text.strip().lower() in ["اشتراك", "💳 الاشتراك"]:
        return

    # تجاهل أزرار القائمة
    if msg.text in ["✨ إنشاء إعلان", "📌 رصيدي", "💳 الاشتراك"]:
        return

    user_id = msg.from_user.id
    user = get_user(user_id)

    if not user:
        add_user(user_id, FREE_POSTS)
        user = get_user(user_id)

    credits_val = user[1]
    sub = is_subscriber(user_id)

    # انتهى الرصيد
    if not sub and credits_val <= 0:
        await msg.answer(
            "❌ <b>انتهى رصيدك المجاني</b>\n\n"
            "🔥 أعجبك مستوى الإعلانات؟\n"
            "يمكنك المتابعة بدون انقطاع عبر الباقات المدفوعة.\n\n"
            "💳 <b>الباقات المتاحة:</b>\n"
            "• 30 إعلان = <b>5$</b>\n"
            "• اشتراك شهري غير محدود = <b>8$</b>\n\n"
            "📩 اكتب <b>اشتراك</b> لمعرفة طريقة التفعيل.",
            parse_mode="HTML",
        )
        return

    # خصم إعلان واحد إذا لم يكن مشتركًا
    if not sub:
        update_credits(user_id, credits_val - 1)

    await msg.answer("⏳ جاري توليد الإعلان...")

    text = generate_ads(msg.text) if ai_ready() else "⚠️ GROQ_API_KEY غير مضاف."

    await msg.answer(
        "✨ <b>الإعلانات المقترحة:</b>\n\n"
        f"{text}\n\n"
        "— — — — —\n"
        "✏️ بدك نعدّل الإعلان؟\n"
        "اكتب مثلاً:\n"
        "• <i>قصّره</i>\n"
        "• <i>خلّيه أقوى</i>\n"
        "• <i>غيّر اللهجة</i>\n"
        "• <i>أضف سعر وCTA</i>\n\n"
        "💡 أو اكتب وصف جديد لإنشاء إعلان آخر.",
        parse_mode="HTML",
    )
