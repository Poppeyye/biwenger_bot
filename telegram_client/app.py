import asyncio
import logging
import os

from biwenger.notices import MarketNotice, TransfersNotice, RoundsNotice
from biwenger.league_logic import BiwengerApi

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError("Incompatible version")
from telegram.ext import Application

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    # Init Client
    biwenger = BiwengerApi(os.getenv("USER_MAIL"), os.getenv("USER_PASS"))
    chat = os.getenv("TELEGRAM_ID_CHAT")
    # Main functionalities
    plys_user = MarketNotice().show(biwenger.get_players_in_market(free=False))
    # Telegram limits every message to 4096 bytes, so we split the message if limit is exceeded
    msgs = [plys_user[i:i + 4096] for i in range(0, len(plys_user), 4096)]
    for text in msgs:
        await application.bot.send_message(chat_id=chat,
                                           text=text,
                                           disable_web_page_preview=True,
                                           parse_mode='Markdown')
    await application.bot.send_message(chat_id=chat, text=TransfersNotice().
                                       show(biwenger.get_last_user_transfers()),
                                       disable_web_page_preview=True,
                                       parse_mode='Markdown')

    await application.bot.send_message(chat_id=chat,
                                       text=MarketNotice().show(biwenger.get_players_in_market(free=True)),
                                       disable_web_page_preview=True,
                                       parse_mode='Markdown')

    await application.bot.send_message(chat_id=chat, text=RoundsNotice().show(biwenger.get_next_round_time()),
                                       disable_web_page_preview=True,
                                       parse_mode='Markdown')


if __name__ == "__main__":
    env_vars = ["TELEGRAM_TOKEN", "TELEGRAM_ID_CHAT", "USER_MAIL", "USER_PASS"]
    for x in env_vars:
        if x not in os.environ:
            logging.error(f'{x} env variable not defined')
            exit(1)

    asyncio.run(main())  # startpoint
