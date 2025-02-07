import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import logging

load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

help_message = """Use one of these commands:
/hello -> Greeting
/help  -> Get more info about commands
"""

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello there! To see what I can do you should run /help!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = Application.builder().token(TELEGRAM_API_TOKEN).build()

    app.add_handler(CommandHandler("hello", hello_command))
    app.add_handler(CommandHandler("help", help_command))

    logging.info("Bot successfully started!")
    app.run_polling(poll_interval=3)
