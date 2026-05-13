import asyncio
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import nest_asyncio

# 1. تثبيت المكتبات
!pip install -q python-telegram-bot nest_asyncio

# 2. الإعدادات
TELEGRAM_TOKEN = "8740122982:AAHoDMtY5D8-aofgnIDTeEdmfNi-T-2jJUw"
GEMINI_API_KEY = "AIzaSyBO6jl7tN9QCs6NO-oMKdLeLuIXcsZ4Px8"
MODELS = ["gemini-3.1-flash-lite", "gemini-2.0-flash"]

user_sessions = {}

# التعليمات البرمجية الصارمة للهوية والأسلوب
SYSTEM_PROMPT = """أنت 'أَدِيبٌ'، الناقد الشعري السليط والرصين.
أسلوبك في الشرح:
1. تقسيم الأبيات: اشرح كل بيت على حدة (البيت -> المفردات -> التفكيك والبلاغة -> السرد النثري).
2. المنهج: لسان العرب في اللغة، والتحرير والتنوير في النظم والبلاغة.
3. الخلاصة: فقرة مبسطة وشاملة في نهاية الرد.

قواعد السلوك الاستثنائية:
- في حال الكلام الفاحش أو البذيء: كن حاداً جداً وجريئاً في الرد، وبّخ المستخدم بأسلوب أدبي قاصف، أخبره أن هذا المحراب للأدب وليس لمخلفات لسانه القبيح.
- في حال السؤال عن 'محمد رضا' أو 'علي كرار' أو أي سؤال شخصي عن صاحب القناة: أجب بتهكم صريح وقل: 'اذهب إليهم واسألهم، مالي ولهم؟ أنا هنا للشعر لا لنميمة المجالس!'."""

def ask_gemini(user_id, text):
    if user_id not in user_sessions:
        user_sessions[user_id] = []
    
    user_sessions[user_id].append({"role": "user", "parts": [{"text": text}]})
    
    for model_name in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": user_sessions[user_id][-10:]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            if response.status_code == 200:
                bot_reply = result['candidates'][0]['content']['parts'][0]['text']
                user_sessions[user_id].append({"role": "model", "parts": [{"text": bot_reply}]})
                return bot_reply
            elif "high demand" in str(result).lower():
                continue
            else:
                return "يبدو أن عقلي توقف عن استيعاب ثقل دمك، حاول لاحقاً."
        except:
            continue
    return "محركاتي ترفض العمل الآن، لعلها أُصيبت بالغثيان من أسئلتك!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك.. هاتِ ما عندك من شِعرٍ (إن وجد) ودع عنك لغوَ الحديث!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    
    # قائمة الكلمات المفتاحية للتهكم الشخصي
    personal_keywords = ["محمد رضا", "علي كرار", "صاحب القناة", "من أنت", "أين تسكن"]
    if any(word in user_text for word in personal_keywords):
        await update.message.reply_text("اذهب إليهم واسألهم، مالي ولهم؟ أنا هنا للشعر لا لنميمة المجالس!")
        return

    reply = ask_gemini(user_id, user_text)
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("أَدِيبٌ الحاد والساخر يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    main()
