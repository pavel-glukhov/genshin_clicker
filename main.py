import asyncio
import logging
import os

from telebot import custom_filters, asyncio_filters

from src.bot import bot
from src.store.scheduler import scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_session_folder():
    directory = "sessions"
    
    if not os.path.exists(directory):
        os.makedirs(directory)


if __name__ == "__main__":
    try:
        create_session_folder()
        scheduler.start()
        logger.info("Starting Bot")
        bot.add_custom_filter(asyncio_filters.StateFilter(bot))
        asyncio.run(bot.polling(skip_pending=True))
    except KeyboardInterrupt:
        logger.info('The bot has been stopped.')
