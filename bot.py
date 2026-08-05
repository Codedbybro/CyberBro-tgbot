import os
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
import requests
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🏠 Главное меню", "🎵 Музыка"],
        ["ℹ️ О боте", "🌦 Погода"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🤖 Добро пожаловать в CyberBro!\n\nВыберите раздел:",
        reply_markup=reply_markup
    )

async def about(update: Update, Context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 CyberBro\n\n"
        "CyberBro — это мой Telegram-бот, который постепенно становится "
        "полезным помощником.\n\n"
        "Скоро здесь появятся:\n"
        "🎵 Музыка\n"
        "🌦 Погода\n"
        "🛠 Полезные инструменты\n\n"
        "Спасибо, что пользуетесь ботом ❤️"
    )        
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:
        await update.message.reply_text(
            "Использование:\n/weather Москва"
        )
        return

    city = " ".join(context.args)
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url)
    await update.message.reply_text(response.text)
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.Regex("^ℹ️ О боте$"),
        about
    )
)
app.add_handler(CommandHandler("weather", weather))
app.run_polling()
