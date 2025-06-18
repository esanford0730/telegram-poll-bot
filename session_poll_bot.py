import os
from datetime import datetime, timedelta
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Helper function to get next Monday's date and the week dates for poll options
def get_next_week_dates():
    today = datetime.utcnow().date()
    days_ahead = (7 - today.weekday()) % 7  # days until next Monday (0=Monday)
    if days_ahead == 0:
        days_ahead = 7  # if today is Monday, get next Monday (not today)
    next_monday = today + timedelta(days=days_ahead)
    week_dates = [(next_monday + timedelta(days=i)) for i in range(7)]
    return week_dates

async def send_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    week_dates = get_next_week_dates()
    options = [f"{date.strftime('%A %Y-%m-%d')}" for date in week_dates]
    options.append("FFA")  # Add 8th choice
    await context.bot.send_poll(
        chat_id=chat_id,
        question="When not available for next session?",
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

async def check_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and "Time to vote for next session" in update.message.text:
        await send_poll(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_trigger))
    print("Bot started. Listening for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()