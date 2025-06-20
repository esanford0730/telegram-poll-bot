import os
import asyncio
import logging
from datetime import datetime, timedelta

from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Environment config ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Helper: Next Week Dates ---
def get_next_week_dates():
    today = datetime.utcnow().date()
    days_ahead = (7 - today.weekday()) % 7 or 7
    next_monday = today + timedelta(days=days_ahead)
    return [next_monday + timedelta(days=i) for i in range(7)]

# --- Poll Trigger ---
async def send_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    week_dates = get_next_week_dates()
    options = [date.strftime("%A %Y-%m-%d") for date in week_dates]
    options.append("FFA")
    await context.bot.send_poll(
        chat_id=chat_id,
        question="When not available for next session?",
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

# --- Telegram Message Handler ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip().lower()
    if text == "are you up son":
        await update.message.reply_text("I'm awake I swear")
    elif "time to vote for next session" in text:
        await send_poll(update, context)

# --- Webhook HTTP Server ---
async def handle_http(request):
    return web.Response(text="Bot is running")

async def run_http_server(app):
    aio_app = web.Application()
    aio_app.add_routes([
        web.get("/", handle_http),
        web.post("/webhook", app.webhook_handler()),
    ])
    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Web server running on port {PORT}")

# --- Main Entry ---
async def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(lambda a: a.bot.set_webhook(WEBHOOK_URL))
        .build()
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    await run_http_server(app)
    await app.initialize()
    await app.start()
    logger.info("Bot is ready and listening for webhook events...")
    await app.updater.start_polling()
    await app.updater.idle()

# --- Start ---
if __name__ == "__main__":
    asyncio.run(main())