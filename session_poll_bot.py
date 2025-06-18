from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta
import calendar
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
TRIGGER_TEXT = 'Time to vote'

def get_upcoming_week_dates():
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    next_monday = today + timedelta(days=days_until_monday)
    week = [(next_monday + timedelta(days=i)) for i in range(7)]
    return [f"{calendar.day_name[d.weekday()]} {d.strftime('%m/%d')}" for d in week]

async def handle_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip().lower()
    if message_text == TRIGGER_TEXT:
        poll_question = "When not available for next session?"
        options = get_upcoming_week_dates() + ["FFA"]
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=poll_question,
            options=options,
            allows_multiple_answers=True,
            is_anonymous=False
        )

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_poll))
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
