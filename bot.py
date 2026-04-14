import os
from flask import Flask, request
from telegram import Update, Bot, ChatPermissions
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)

app = Flask(__name__)

bad_words = ["سب", "كلمة1", "كلمة2"]

warnings = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)
    key = f"{chat_id}_{user_id}"

    text = message.text.lower()

    if any(w in text for w in bad_words):

        warnings[key] = warnings.get(key, 0) + 1

        try:
            await message.delete()
        except:
            pass

        if warnings[key] == 1:
            await message.reply_text("⚠️ إنذار 1")
        elif warnings[key] == 2:
            await message.reply_text("⚠️ إنذار 2")
        else:
            await message.chat.restrict_member(
                message.from_user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await message.reply_text("🚫 تم الكتم نهائياً")

application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"
