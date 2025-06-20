import os
import asyncio
from datetime import datetime, timedelta

from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# Load from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-app.onrender.com/webhook
PORT = int(os.getenv("PORT", "10000"))

# Generate poll options
def get_next_week_dates():
    today = datetime.utcnow().date()
    days_ahead = (7 - today.weekday()) % 7 or 7
    monday = today + timedelta(days=days_ahead)
    return [(monday + timedelta(days=i)) for i in range(7)]

# Main message logic
async def check_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "time to vote for next session" in text:
        await send_poll(update, context)
    elif "are you up son" in text:
        await update.message.reply_text("I'm awake I swear")

# Poll logic
async def send_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dates = get_next_week_dates()
    options = [f"{d.strftime('%A')} {d.month}/{d.day}" for d in dates] + ["FFA"]
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question="When not available for next session?",
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

# /restart
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Restarting bot...")
    raise SystemExit()

# Ping for Render's port scanner
async def handle_healthcheck(request):
    return web.Response(text="OK", status=200)

# Main async launch
async def main():
    import logging
    logging.basicConfig(level=logging.INFO)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_trigger))
    app.add_handler(CommandHandler("restart", restart))

    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()

    # Bind aiohttp app explicitly for Render
    aio_app = app.web_app
    aio_app.router.add_get("/", handle_healthcheck)  # ping path
    aio_app.router.add_post("/webhook", app.update_queue_asgi)  # ensure POST works too

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port=PORT)
    print(f"✅ Starting webhook server on port {PORT}")
    await site.start()

    # Keep alive until manually stopped
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())