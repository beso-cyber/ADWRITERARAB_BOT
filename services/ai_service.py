from groq import Groq
from config import GROQ_API_KEY


_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def ai_ready() -> bool:
    return _client is not None


def generate_ads(text: str) -> str:
    if not _client:
        return "⚠️ خدمة الذكاء الاصطناعي غير مفعّلة حالياً. أضف GROQ_API_KEY ثم أعد تشغيل البوت."

    prompt = f"اكتب 5 بوستات إعلانية جذابة باللغة العربية الفصحى عن: {text}"

    resp = _client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=650,
    )
    return resp.choices[0].message.content
