import asyncio
import logging
import os

from biwenger.notices import MarketNotice, TransfersNotice
from biwenger.session import BiwengerApi

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError("Incompatible version")
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)
        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.effective_message.reply_text(text)


async def init_biwenger_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    biwenger = BiwengerApi('alvarito174@hotmail.com', os.getenv("USER_PASS"))
    # await update.message.reply_text('[tag](link))', parse_mode='MarkdownV2')
    await update.message.reply_text(MarketNotice().show(biwenger.get_players_in_market()), parse_mode='Markdown')
    await update.message.reply_text(TransfersNotice().show(biwenger.get_last_user_transfers()), parse_mode='Markdown')


async def run_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    context.job_queue.run_repeating(alarm, interval=5, chat_id=chat_id, name=str(chat_id))
    text = "Timer successfully set!"
    await update.effective_message.reply_text(text)


async def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    # on different commands - answer in Telegram
    biwenger = BiwengerApi('alvarito174@hotmail.com', os.getenv("USER_PASS"))
    private_chat = '855531130'
    group_chat = '-1001673290336'
    #await application.bot.send_message(chat_id='855531130', text='<a href="#"><span class="tg-spoiler">spoiler</span> </a>',parse_mode='HTML')

    await application.bot.send_message(chat_id=group_chat, text=MarketNotice().
                                       show(biwenger.get_players_in_market()),
                                       disable_web_page_preview=True,
                                       parse_mode='Markdown')
    await application.bot.send_message(chat_id=group_chat, text=TransfersNotice().
                                       show(biwenger.get_last_user_transfers()),
                                       disable_web_page_preview=True,
                                       parse_mode='Markdown')
    # application.add_handler(CommandHandler("biwenger", init_biwenger_session))
    # application.add_handler(CommandHandler("run_task", run_task))


# Run the bot until the user presses Ctrl-C
    #application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
    #asyncio.run(send_message_to_chat_id())