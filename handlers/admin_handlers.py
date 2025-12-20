from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from database import (
    get_users_count,
    get_all_users,
    get_user,
    update_credits,
)

from keyboards.admin_kb import admin_menu
from keyboards.user_kb import user_menu

router = Router()

# ================= حالات المدير =================
class AdminStates(StatesGroup):
    add_credit = State()
    deduct_credit = State()
    broadcast = State()


def is_admin(msg: Message) -> bool:
    return msg.from_user and msg.from_user.id == ADMIN_ID


# ================= لوحة المدير =================
@router.message(Command("admin"))
async def admin_panel(msg: Message):
    if not is_admin(msg):
        await msg.answer("❌ هذا الأمر مخصص للمدير فقط.")
        return

    await msg.answer(
        "👑 <b>لوحة تحكم المدير</b>\n\nاختر إجراء:",
        reply_markup=admin_menu(),
        parse_mode="HTML",
    )


# ================= رجوع للقائمة =================
@router.message(F.text == "↩️ رجوع للقائمة الرئيسية")
async def back_to_menu(msg: Message, state: FSMContext):
    if not is_admin(msg):
        return
    await state.clear()
    await msg.answer("✅ تم الرجوع للقائمة الرئيسية.", reply_markup=user_menu())


# ================= عدد المستخدمين =================
@router.message(F.text == "📊 عدد المستخدمين")
async def users_count(msg: Message):
    if not is_admin(msg):
        return

    count = get_users_count()
    await msg.answer(f"📊 عدد المستخدمين الحالي:\n<b>{count}</b>", parse_mode="HTML")


# ================= إضافة رصيد =================
@router.message(F.text == "➕ إضافة رصيد")
async def add_credit_start(msg: Message, state: FSMContext):
    if not is_admin(msg):
        return

    await state.set_state(AdminStates.add_credit)
    await msg.answer(
        "✏️ أرسل البيانات بهذا الشكل:\n\n"
        "<code>USER_ID AMOUNT</code>\n"
        "مثال:\n<code>123456789 10</code>",
        parse_mode="HTML",
    )


@router.message(AdminStates.add_credit)
async def add_credit_apply(msg: Message, state: FSMContext):
    if not is_admin(msg):
        return

    try:
        user_id, amount = map(int, msg.text.split())
        user = get_user(user_id)

        if not user:
            await msg.answer("❌ المستخدم غير موجود.")
            return

        new_credits = user[1] + amount
        update_credits(user_id, new_credits)

        await msg.answer(
            f"✅ تم إضافة الرصيد بنجاح.\n\n"
            f"ID: <code>{user_id}</code>\n"
            f"الرصيد الجديد: <b>{new_credits}</b>",
            parse_mode="HTML",
        )
        await state.clear()

    except Exception:
        await msg.answer("❌ الصيغة غير صحيحة. مثال:\n<code>123456789 10</code>", parse_mode="HTML")


# ================= خصم رصيد =================
@router.message(F.text == "➖ خصم رصيد")
async def deduct_credit_start(msg: Message, state: FSMContext):
    if not is_admin(msg):
        return

    await state.clear()
    await state.set_state(AdminStates.deduct_credit)
    await msg.answer(
        "✏️ أرسل البيانات بهذا الشكل:\n\n"
        "<code>USER_ID AMOUNT</code>\n"
        "مثال:\n<code>123456789 5</code>",
        parse_mode="HTML",
    )


@router.message(AdminStates.deduct_credit, F.text.regexp(r"^\d+\s+\d+$"))
async def deduct_credit_apply(msg: Message, state: FSMContext):
    if not is_admin(msg):
        return

    try:
        user_id, amount = map(int, msg.text.split())
        user = get_user(user_id)

        if not user:
            await msg.answer("❌ المستخدم غير موجود.")
            return

        new_credits = max(0, user[1] - amount)
        update_credits(user_id, new_credits)

        await msg.answer(
            f"✅ تم خصم الرصيد.\n\n"
            f"ID: <code>{user_id}</code>\n"
            f"الرصيد الجديد: <b>{new_credits}</b>",
            parse_mode="HTML",
        )
        await state.clear()

    except Exception:
        await msg.answer("❌ الصيغة غير صحيحة. مثال:\n<code>123456789 5</code>", parse_mode="HTML")


# ================= رسالة جماعية =================
@router.message(F.text == "📢 رسالة جماعية")
async def broadcast_start(msg: Message, state: FSMContext):
    if not is_admin(msg):
        return

    await state.clear()
    await state.set_state(AdminStates.broadcast)
    await msg.answer("✉️ أرسل الآن نص الرسالة الجماعية (سيتم الإرسال فورًا).")


@router.message(AdminStates.broadcast, ~F.text.startswith("📢"))
async def broadcast_apply(msg: Message, state: FSMContext):
    if not is_admin(msg):
        return

    users = get_all_users()
    success, failed = 0, 0

    for user_id in users:
        try:
            await msg.bot.send_message(user_id, msg.text)
            success += 1
        except Exception:
            failed += 1

    await msg.answer(
        f"✅ تم إرسال الرسالة الجماعية\n\n"
        f"📤 تم الإرسال إلى: {success}\n"
        f"❌ فشل الإرسال إلى: {failed}"
    )
    await state.clear()
