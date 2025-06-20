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
    Application,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-service.onrender.com/webhook
PORT = int(os.getenv("PORT", "10000"))


def get_next_week_dates():
    today = datetime.utcnow().date()
    days_ahead = (7 - today.weekday()) % 7 or 7
    monday = today + timedelta(days=days_ahead)
    return [(monday + timedelta(days=i)) for i in range(7)]


async def check_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()
    if "time to vote for next session" in msg:
        await send_poll(update, context)
    elif "are you up son" in msg:
        await update.message.reply_text("I'm awake I swear")


async def send_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    dates = get_next_week_dates()
    options = [f"{d.strftime('%A')} {d.month}/{d.day}" for d in dates] + ["FFA"]
    await context.bot.send_poll(
        chat_id=chat_id,
        question="When not available for next session?",
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Restarting bot...")
    raise SystemExit()


# --- aiohttp handlers --- #
async def handle_healthcheck(request):
    return web.Response(text="OK", status=200)


async def create_app():
    import logging
    logging.basicConfig(level=logging.INFO)

    # Set up Telegram application
    telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_trigger))
    telegram_app.add_handler(CommandHandler("restart", restart))

    # Initialize and set webhook
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()

    # Set up aiohttp server
    aio_app = web.Application()
    aio_app.router.add_get("/", handle_healthcheck)
    aio_app.router.add_post("/webhook", telegram_app.update_queue_asgi)

    return aio_app


async def main():
    app = await create_app()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    print(f"✅ Webhook server listening on port {PORT}")
    await site.start()

    # Run forever
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())