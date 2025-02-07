import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import logging

load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

help_message = """Use one of these commands:
/hello      -> Greeting
/help       -> Get more info about commands
/polltest   -> Test if the poll works
"""

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello there! To see what I can do you should run /help!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_message)

async def test_poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="yes"),
            InlineKeyboardButton("No", callback_data="no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Do you think the poll works?", reply_markup = reply_markup)

async def test_poll_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data
    logging.info(f"User chose: {choice}")

    await query.edit_message_text(text=f"You chose: '{choice}'.The poll worked.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = Application.builder().token(TELEGRAM_API_TOKEN).build()

    app.add_handler(CommandHandler("hello", hello_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("polltest", test_poll_command))

    app.add_handler(CallbackQueryHandler(test_poll_callback))

    app.run_polling(poll_interval=3)
