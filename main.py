import logging
import os

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers.user_handlers import router as user_router
from handlers.admin_handlers import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ✅ هذا هو المتغير الذي يبحث عنه uvicorn
app = FastAPI()

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(admin_router)
dp.include_router(user_router)


@app.on_event("startup")
async def on_startup():
    init_db()

    # حذف أي webhook قديم
    await bot.delete_webhook(drop_pending_updates=True)

    # Render يضع الرابط تلقائيًا
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    webhook_url = f"{render_url}/webhook"

    await bot.set_webhook(webhook_url)
    logger.info(f"🚀 Webhook set to: {webhook_url}")


@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}
