import os
import asyncio
from datetime import datetime, timedelta

from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
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
    options.append("FFA")  # 8th choice
    await context.bot.send_poll(
        chat_id=chat_id,
        question="When not available for next session?",
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )


async def check_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if "time to vote for next session" in update.message.text.lower():
            await send_poll(update, context)


async def handle_http_request(request):
    return web.Response(text="Bot is running")


async def start_web_server():
    app = web.Application()
    app.add_routes([web.get("/", handle_http_request)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()


def main():
    import logging
    logging.basicConfig(level=logging.INFO)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_trigger))

    async def startup():
        # Delete webhook if set, to avoid conflict errors on polling
        await app.bot.delete_webhook()

    app.post_init = startup

    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())

    print("Bot started. Listening for messages...")
    app.run_polling()


if __name__ == "__main__":
    main()