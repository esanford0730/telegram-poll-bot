import logging
import os
import json
import time
import subprocess
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, Poll, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_sessions = {}

BUTTONS = [
    ["Today", "Tomorrow"],
    ["No Preference"],
]

REPLY_MARKUP = ReplyKeyboardMarkup(
    [[KeyboardButton(text=btn) for btn in row] for row in BUTTONS],
    resize_keyboard=True,
    one_time_keyboard=True,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "When are you available to game?", reply_markup=REPLY_MARKUP
    )

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    response = update.message.text.strip()
    user_sessions[user_id] = response
    logger.info(f"Received response from {user_id}: {response}")
    await update.message.reply_text("Got it!")

async def results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    counts = {"Today": 0, "Tomorrow": 0, "No Preference": 0}
    for vote in user_sessions.values():
        if vote in counts:
            counts[vote] += 1

    result_text = "\n".join([f"{k}: {v}" for k, v in counts.items()])
    await update.message.reply_text(f"Current Results:\n{result_text}")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions.clear()
    await update.message.reply_text("Cleared all votes.")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Restarting bot...")
    raise SystemExit()

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("results", results))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_response))

    logger.info("Bot started. Listening for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()