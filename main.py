import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import logging
import pika
import threading
import asyncio
import json

load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
RABBITMQ_APPROVAL_QUEUE = os.getenv("RABBITMQ_APPROVAL_QUEUE")
RABBITMQ_APPROVED_QUEUE = os.getenv("RABBITMQ_APPROVED_QUEUE")

help_message = """Use one of these commands:
/hello      -> Greeting
/help       -> Get more info about commands
"""

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello there! To see what I can do you should run /help!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_message)

async def send_approval_message(context: ContextTypes.DEFAULT_TYPE, repo_name: str):
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=f"approved {repo_name}"),
            InlineKeyboardButton("No", callback_data=f"denied {repo_name}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=f"Do you want to create the repo '{repo_name}'?",
        reply_markup=reply_markup
    )

async def approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    approved = data.startswith("approved")
    repo_name = data.split(" ")[1]

    if approved:
        logging.info(f"User approved repo: {repo_name}")

        message = json.dumps({"repo_name": repo_name}).encode("utf-8")

        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_APPROVED_QUEUE, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_APPROVED_QUEUE,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()

        await query.edit_message_text(text=f"Creation of repository '{repo_name}' approved.")
    else:
        await query.edit_message_text(text=f"Creation of repository '{repo_name}' denied.")

def rabbitmq_consumer(application: Application, loop: asyncio.AbstractEventLoop):
    def callback(ch, method, properties, body):
        try:
            message = json.loads(body.decode("utf-8"))
            repo_name = message.get("repo_name")

            if repo_name:
                logging.info(f"Received approval request for repo: {repo_name}")
                asyncio.run_coroutine_threadsafe(
                    send_approval_message(context=application, repo_name=repo_name),
                    loop
                )
            else:
                logging.warning("Received invalid message format.")

        except Exception as e:
            logging.error(f"Encountered Exception: {e}")

    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_APPROVAL_QUEUE, durable=True)
    channel.basic_consume(queue=RABBITMQ_APPROVAL_QUEUE, on_message_callback=callback, auto_ack=True)

    logging.info("RabbitMQ consumer started...")
    channel.start_consuming()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(TELEGRAM_API_TOKEN).build()

    app.add_handler(CommandHandler("hello", hello_command))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(CallbackQueryHandler(approval_callback))

    rabbitmq_thread = threading.Thread(
        target=rabbitmq_consumer,
        args=(app, loop),
        daemon=True
    )
    rabbitmq_thread.start()

    app.run_polling(poll_interval=3)
