import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://yourapp.onrender.com/webhook
PORT = int(os.getenv("PORT", 10000))

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility to get date options for the poll
def get_next_week_dates():
    today = datetime.utcnow().date()
    days_ahead = (7 - today.weekday()) % 7 or 7
    next_monday = today + timedelta(days=days_ahead)
    return [next_monday + timedelta(days=i) for i in range(7)]

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm awake. Say 'are you up son' or 'time to vote for next session'.")

# General message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()
    logger.info(f"Received message: {text}")

    if text == "are you up son":
        await update.message.reply_text("I'm awake I swear")
    elif "time to vote for next session" in text:
        week_dates = get_next_week_dates()
        options = [date.strftime("%A %Y-%m-%d") for date in week_dates]
        options.append("FFA")
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question="When not available for next session?",
            options=options,
            is_anonymous=False,
            allows_multiple_answers=True,
        )

# Main setup function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting webhook...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()