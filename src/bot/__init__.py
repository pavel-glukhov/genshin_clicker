import os
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from dotenv import load_dotenv

from src.bot.keyboards import create_reply_keyboard_buttons

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
dotenv_path = os.path.join(ROOT_PATH, '.env')
load_dotenv(dotenv_path)
state_storage = StateMemoryStorage()

bot = AsyncTeleBot(os.getenv('TELEGRAM_TOKEN'),
                   state_storage=state_storage)

from . import auth, awards, common, set_datetime
