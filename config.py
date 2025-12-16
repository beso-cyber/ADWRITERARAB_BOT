import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
FREE_POSTS = int(os.getenv("FREE_POSTS", 3))

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في ملف .env")
