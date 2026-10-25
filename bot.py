# ============================================================
# CYBERBRO
# Полезный Telegram-бот
#
# Функции:
#   /start
#   Главное меню
#   Погода
#   Калькулятор
#   Генератор паролей
#   Информация о боте
#   Полезные команды
#   Проверка IP / домена
#
# Стек:
#   Python
#   python-telegram-bot
#   requests
#   python-dotenv
#
# Переменные:
#   BOT_TOKEN=токен_бота
# ============================================================


# ============================================================
# ИМПОРТЫ
# ============================================================

import os
import re
import secrets
import string
import logging
import asyncio
import ast
import operator

import requests

from dotenv import load_dotenv

from telegram import (
    Update,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# ============================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# Safe arithmetic evaluator: allow a small AST subset instead of eval().
_CALC_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_calculate(expression: str):
    if len(expression) > 100:
        raise ValueError("Expression is too long")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 10**12:
                raise ValueError("Number is too large")
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _CALC_OPERATORS:
            return _CALC_OPERATORS[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _CALC_OPERATORS:
            return _CALC_OPERATORS[type(node.op)](evaluate(node.operand))
        raise ValueError("Unsupported expression")

    result = evaluate(tree)
    if isinstance(result, (int, float)) and abs(result) > 10**15:
        raise ValueError("Result is too large")
    return result



# ============================================================
# ЗАГРУЖАЕМ .ENV
# ============================================================

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


# ============================================================
# ПРОВЕРЯЕМ ТОКЕН
# ============================================================

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не найден. "
        "Добавь его в файл .env"
    )


# ============================================================
# КЛАВИАТУРА
# ============================================================

MAIN_KEYBOARD = [
    ["🌤 Погода", "🧮 Калькулятор"],
    ["🔐 Пароль", "🌐 IP / Домен"],
    ["ℹ️ О боте", "🛠 Инструменты"],
]


main_keyboard = ReplyKeyboardMarkup(
    MAIN_KEYBOARD,
    resize_keyboard=True,
    input_field_placeholder="Выберите раздел...",
)


# ============================================================
# /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Главное приветствие.
    """

    text = (
        "⚡ <b>CyberBro</b>\n\n"
        "Полезный Telegram-помощник для повседневных задач.\n\n"

        "Здесь можно:\n"
        "• посмотреть погоду\n"
        "• быстро посчитать выражение\n"
        "• создать случайный пароль\n"
        "• проверить IP или домен\n"
        "• открыть список инструментов\n\n"

        "Выберите нужный раздел ниже."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_keyboard,
    )


# ============================================================
# КНОПКА «О БОТЕ»
# ============================================================

async def about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Информация о CyberBro.
    """

    text = (
        "ℹ️ <b>CyberBro</b>\n\n"

        "CyberBro — персональный Telegram-проект, "
        "который развивается как набор полезных "
        "инструментов в одном месте.\n\n"

        "<b>Технологии:</b>\n"
        "Python • Telegram API • HTTP • Linux\n\n"

        "<b>Доступно сейчас:</b>\n"
        "🌤 Погода\n"
        "🧮 Калькулятор\n"
        "🔐 Генератор паролей\n"
        "🌐 Проверка IP / домена\n"
        "🛠 Полезные инструменты\n\n"

        "Проект развивается постепенно."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# ПОГОДА
# ============================================================

async def weather(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Показывает погоду через wttr.in.

    Пример:
        /weather Москва
    """

    if not context.args:
        await update.message.reply_text(
            "🌤 <b>Погода</b>\n\n"
            "Использование:\n"
            "<code>/weather Москва</code>\n\n"
            "Например:\n"
            "<code>/weather Пятигорск</code>",
            parse_mode="HTML",
        )
        return


    city = " ".join(context.args)

    url = (
        f"https://wttr.in/"
        f"{requests.utils.quote(city)}"
        f"?format=3"
    )

    try:

        response = await asyncio.to_thread(requests.get, url, timeout=10)

        response.raise_for_status()

        await update.message.reply_text(
            f"🌤 <b>{city}</b>\n\n"
            f"<code>{response.text}</code>",
            parse_mode="HTML",
        )

    except requests.RequestException:

        await update.message.reply_text(
            "❌ Не удалось получить погоду.\n"
            "Попробуйте ещё раз немного позже."
        )


# ============================================================
# КАЛЬКУЛЯТОР
# ============================================================

async def calculate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Простой калькулятор.

    Пример:
        /calc 25 * 4
    """

    if not context.args:

        await update.message.reply_text(
            "🧮 <b>Калькулятор</b>\n\n"
            "Пример:\n"
            "<code>/calc 25 * 4</code>\n\n"
            "Или:\n"
            "<code>/calc 100 / 5 + 7</code>",
            parse_mode="HTML",
        )

        return


    expression = " ".join(context.args)


    # Разрешаем только цифры и базовые математические символы.
    if not re.fullmatch(
        r"[0-9+\-*/().%\s]+",
        expression,
    ):

        await update.message.reply_text(
            "❌ Выражение содержит недопустимые символы."
        )

        return


    try:

        result = safe_calculate(expression)

        await update.message.reply_text(
            f"🧮 <b>{expression}</b>\n\n"
            f"= <code>{result}</code>",
            parse_mode="HTML",
        )

    except Exception:

        await update.message.reply_text(
            "❌ Не удалось вычислить выражение."
        )


# ============================================================
# ГЕНЕРАТОР ПАРОЛЯ
# ============================================================

async def password(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Генерирует случайный пароль.

    По умолчанию: 16 символов.

    Можно:
        /password 24
    """

    length = 16

    if context.args:

        try:
            length = int(context.args[0])

        except ValueError:

            await update.message.reply_text(
                "❌ Длина должна быть числом."
            )

            return


    if length < 6 or length > 128:

        await update.message.reply_text(
            "❌ Используйте длину от 6 до 128 символов."
        )

        return


    alphabet = (
        string.ascii_letters
        + string.digits
        + "!@#$%^&*_-+="
    )


    generated = "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


    await update.message.reply_text(
        "🔐 <b>Сгенерированный пароль</b>\n\n"
        f"<code>{generated}</code>\n\n"
        "Не отправляйте пароль посторонним.",
        parse_mode="HTML",
    )


# ============================================================
# IP / ДОМЕН
# ============================================================

async def ip_info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Показывает базовую информацию
    по IP или домену.

    Пример:
        /ip google.com
    """

    if not context.args:

        await update.message.reply_text(
            "🌐 <b>IP / Домен</b>\n\n"
            "Использование:\n"
            "<code>/ip example.com</code>",
            parse_mode="HTML",
        )

        return


    host = context.args[0].strip()

    url = (
        "https://ipwho.is/"
        + requests.utils.quote(host)
    )


    try:

        response = await asyncio.to_thread(requests.get, url, timeout=10)

        response.raise_for_status()
        data = response.json()


        if not data.get("success", False):

            await update.message.reply_text(
                "❌ Не удалось определить информацию."
            )

            return


        message = (
            "🌐 <b>Информация</b>\n\n"
            f"IP: <code>{data.get('ip', '—')}</code>\n"
            f"Страна: {data.get('country', '—')}\n"
            f"Город: {data.get('city', '—')}\n"
            f"Провайдер: {data.get('connection', {}).get('isp', '—')}\n"
            f"Организация: {data.get('connection', {}).get('org', '—')}"
        )


        await update.message.reply_text(
            message,
            parse_mode="HTML",
        )


    except requests.RequestException:

        await update.message.reply_text(
            "❌ Ошибка при обращении к сервису."
        )


# ============================================================
# ПОЛЕЗНЫЕ ИНСТРУМЕНТЫ
# ============================================================

async def tools(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Список инструментов.
    """

    text = (
        "🛠 <b>Инструменты CyberBro</b>\n\n"

        "🌤 <code>/weather город</code>\n"
        "Получить текущую погоду.\n\n"

        "🧮 <code>/calc выражение</code>\n"
        "Посчитать математическое выражение.\n\n"

        "🔐 <code>/password 16</code>\n"
        "Создать случайный пароль.\n\n"

        "🌐 <code>/ip example.com</code>\n"
        "Получить базовую информацию об IP/домене."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# ОБРАБОТКА КНОПОК
# ============================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает обычные кнопки клавиатуры.
    """

    text = update.message.text


    if text == "🌤 Погода":

        await update.message.reply_text(
            "🌤 Напишите город.\n\n"
            "Например:\n"
            "<code>/weather Москва</code>",
            parse_mode="HTML",
        )

        return


    if text == "🧮 Калькулятор":

        await update.message.reply_text(
            "🧮 Введите выражение командой:\n"
            "<code>/calc 25 * 4</code>",
            parse_mode="HTML",
        )

        return


    if text == "🔐 Пароль":

        await update.message.reply_text(
            "🔐 Создам случайный пароль.\n\n"
            "Например:\n"
            "<code>/password 20</code>",
            parse_mode="HTML",
        )

        return


    if text == "🌐 IP / Домен":

        await update.message.reply_text(
            "🌐 Введите:\n"
            "<code>/ip example.com</code>",
            parse_mode="HTML",
        )

        return


    if text == "ℹ️ О боте":

        await about(update, context)

        return


    if text == "🛠 Инструменты":

        await tools(update, context)

        return

    await unknown(update, context)


# ============================================================
# НЕИЗВЕСТНАЯ КОМАНДА / ТЕКСТ
# ============================================================

async def unknown(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Ответ на неизвестный текст.
    """

    await update.message.reply_text(
        "Не совсем понял команду.\n\n"
        "Используйте /start, чтобы открыть "
        "главное меню."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # Создаём приложение Telegram-бота.
    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )


    # --------------------------------------------------------
    # COMMAND HANDLERS
    # --------------------------------------------------------

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )


    app.add_handler(
        CommandHandler(
            "about",
            about,
        )
    )


    app.add_handler(
        CommandHandler(
            "weather",
            weather,
        )
    )


    app.add_handler(
        CommandHandler(
            "calc",
            calculate,
        )
    )


    app.add_handler(
        CommandHandler(
            "password",
            password,
        )
    )


    app.add_handler(
        CommandHandler(
            "ip",
            ip_info,
        )
    )


    app.add_handler(
        CommandHandler(
            "tools",
            tools,
        )
    )


    # --------------------------------------------------------
    # ОБЫЧНЫЕ КНОПКИ
    # --------------------------------------------------------

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            button_handler,
        )
    )


    # --------------------------------------------------------
    # ЗАПУСК
    # --------------------------------------------------------

    print("CyberBro запущен.")

    app.run_polling()


# ============================================================
# ТОЧКА ВХОДА
# ============================================================

if __name__ == "__main__":
    main()
