import os
import json
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔑 حط التوكن في Environment Variable في Render
TOKEN = os.getenv("TOKEN")

bad_words = ["قع", "زب", "قحبة","نيك","نكمك", "بزازل"]

DATA_FILE = "warnings.json"

# تحميل الإنذارات
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# حفظ الإنذارات
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

warnings = load_data()

# معالجة الرسائل
async def moderate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)
    key = f"{chat_id}_{user_id}"

    text = message.text.lower()

    if any(word in text for word in bad_words):

        warnings[key] = warnings.get(key, 0) + 1
        save_data(warnings)

        try:
            await message.delete()
        except:
            pass

        if warnings[key] == 1:
            await message.chat.send_message("⚠️ إنذار 1")

        elif warnings[key] == 2:
            await message.chat.send_message("⚠️ إنذار 2")

        else:
            await message.chat.restrict_member(
                message.from_user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await message.chat.send_message("🚫 تم كتمك نهائياً")

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderate))

print("Bot is running...")
app.run_polling()
