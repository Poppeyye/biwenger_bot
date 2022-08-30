import asyncio
import logging
import os

from biwenger.notices import MarketNotice, TransfersNotice, MatchNotice, RoundsNotice
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


"""
Example of command handler
async def init_biwenger_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    biwenger = BiwengerApi('alvarito174@hotmail.com', os.getenv("USER_PASS"))
    # await update.message.reply_text('[tag](link))', parse_mode='MarkdownV2')
    await update.message.reply_text(MarketNotice().show(biwenger.get_players_in_market()), parse_mode='Markdown')
    await update.message.reply_text(TransfersNotice().show(biwenger.get_last_user_transfers()), parse_mode='Markdown')
    """


async def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    # on different commands - answer in Telegram
    biwenger = BiwengerApi('alvarito174@hotmail.com', os.getenv("USER_PASS"))
    private_chat = '855531130'
    group_chat = '-1001673290336'
    chat = group_chat

    await application.bot.send_message(chat_id=chat,
                                       text=MarketNotice().show(biwenger.get_players_in_market(free=True)),
                                       disable_web_page_preview=True,
                                       parse_mode='Markdown')
    """
    Tiene sentido hacer una encuesta para saber quien va a ganar?
    almacenar resultados y mostrarlos cuando termine la jornada
    await application.bot.send_poll(chat_id= private_chat, question="Quién hará más puntos esta jornada?", 
                                    options=['yo', 'tu'])
    """

    await application.bot.send_message(chat_id=chat,
                                       text=MarketNotice().show(biwenger.get_players_in_market(free=False)),
                                       disable_web_page_preview=True,
                                       parse_mode='Markdown')
    await application.bot.send_message(chat_id=chat, text=TransfersNotice().
                                       show(biwenger.get_last_user_transfers()),
                                       disable_web_page_preview=True,
                                       parse_mode='Markdown')
    await application.bot.send_message(chat_id=chat, text=RoundsNotice().show(biwenger.get_next_round_time()),
                                       disable_web_page_preview=True,
                                       parse_mode='Markdown')
    # application.add_handler(CommandHandler("biwenger", init_biwenger_session))
    # application.add_handler(CommandHandler("run_task", run_task))


# Run the bot until the user presses Ctrl-C
    #application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
    #asyncio.run(send_message_to_chat_id())