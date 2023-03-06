import logging
import os

import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Global variables
content = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_user = update.message.from_user
    text = " ".join(update.message.text.split(" ")[1:])
    content[from_user.id] = [
        {"role": "system", "content": text},
    ]

    logging.info(f"Initialized chatbot for user {from_user.id} with {text}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"You've initialized the chatbot like the following: {text}!"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_user = update.message.from_user
    text = " ".join(update.message.text.split(" ")[1:])

    # Check if user is in content
    if from_user.id not in content:
        content[from_user.id] = [
            {"role": "system", "content": "you are a human"},
        ]

    # Add user message to content
    content[from_user.id].append({"role": "user", "content": text})
    logging.info(f"User {from_user.id} sent {text}")

    # Generate response
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=content[from_user.id]
    )
    if "choices" not in resp or len(resp["choices"]) == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Internal Server Error"
        )

    message = resp["choices"][0].message.content
    content[from_user.id].append({"role": "assistant", "content": message})
    logging.info(f"Generated response {message} for user {from_user.id}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message
    )


if __name__ == "__main__":
    # Read tokens from environment variables
    openai.api_key = os.getenv("OPENAI_API_KEY")
    telegram_api_key = os.getenv("TELEGRAM_API_KEY")

    # Create application
    application = ApplicationBuilder().token(telegram_api_key).build()

    # Add handlers
    start_handler = CommandHandler("start", start)
    init_handler = CommandHandler("init", init)
    chat_handler = CommandHandler("chat", chat)
    application.add_handler(start_handler)
    application.add_handler(init_handler)
    application.add_handler(chat_handler)

    # Start polling
    application.run_polling()
