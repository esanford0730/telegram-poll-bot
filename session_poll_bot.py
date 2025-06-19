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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. "https://your-app.onrender.com/webhook"
PORT = int(os.getenv("PORT", "8000"))

def get_next_week_dates():
    today = datetime.utcnow().date()
    days_ahead = (7 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    next_monday = today + timedelta(days=days_ahead)
    return [(next_monday + timedelta(days=i)) for i in range(7)]

async def send_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    week_dates = get_next_week_dates()
    options = [f"{date.strftime('%A')} {date.month}/{date.day}" for date in week_dates]
    options.append("FFA")
    await context.bot.send_poll(
        chat_id=chat_id,
        question="When not available for next session?",
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

async def check_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        msg = update.message.text.lower()
        if "time to vote for next session" in msg:
            await send_poll(update, context)
        elif "are you up son" in msg:
            await update.message.reply_text("I'm awake I swear")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Restarting bot...")
    raise SystemExit()

async def handle_healthcheck(request):
    return web.Response(text="Webhook bot is alive!")

async def main():
    import logging
    logging.basicConfig(level=logging.INFO)

    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_trigger))
    app.add_handler(CommandHandler("restart", restart))

    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="/webhook",
        webhook_url=WEBHOOK_URL,
    )

    # Optional: Render healthcheck support
    runner = web.AppRunner(web.Application())
    runner.app.add_routes([web.get("/", handle_healthcheck)])
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()

    print("Bot is running via webhook...")
    await app.updater.wait()

if __name__ == "__main__":
    asyncio.run(main())