import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import (
    auth,
    awards,
    common,
    set_datetime,
    start,
    sign_out,
    status
)
from src.bot.middlewares.auth_middleware import AuthMiddleware
from src.config import load_config
from src.store.scheduler import scheduler

logger = logging.getLogger(__name__)


def create_session_folder():
    ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    directory = os.path.join(ROOT_PATH, "sessions")
    
    if not os.path.exists(directory):
        os.makedirs(directory)


def register_routers(dp):
    dp.include_router(awards.router)
    dp.include_router(auth.router)
    dp.include_router(set_datetime.router)
    dp.include_router(common.router)
    dp.include_router(start.router)
    dp.include_router(sign_out.router)
    dp.include_router(status.router)


def register_middlewares():
    awards.router.message.middleware(AuthMiddleware())
    start.router.message.middleware(AuthMiddleware())
    set_datetime.router.message.middleware(AuthMiddleware())
    common.router.message.middleware(AuthMiddleware())
    sign_out.router.message.middleware(AuthMiddleware())
    status.router.message.middleware(AuthMiddleware())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    config = load_config()
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(config.token)
    
    register_routers(dp)
    register_middlewares()
    create_session_folder()
    scheduler.start()
    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


def cli():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")


if __name__ == '__main__':
    cli()
