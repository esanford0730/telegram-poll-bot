import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-app-name.onrender.com/webhook
PORT = int(os.getenv("PORT", 10000))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_next_week_dates():
    today = datetime.utcnow().date()
    days_ahead = (7 - today.weekday()) % 7 or 7
    next_monday = today + timedelta(days=days_ahead)
    return [next_monday + timedelta(days=i) for i in range(7)]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Booting up peasant brain BEEP BOOP")

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

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Optional: clear existing webhook before setting a new one
    async def reset_webhook():
        await app.bot.delete_webhook()
        await app.bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"Webhook has been reset to: {WEBHOOK_URL}")

    import asyncio
    asyncio.run(reset_webhook())

    logger.info("🚀 Starting webhook server...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()