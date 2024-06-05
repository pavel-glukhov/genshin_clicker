# import os
# from dotenv import load_dotenv
#
# from src.bot.keyboards import create_reply_keyboard_buttons
#
#
# dotenv_path = os.path.join(ROOT_PATH, '.env')
# load_dotenv(dotenv_path)
# state_storage = StateMemoryStorage()
#
# bot = AsyncTeleBot(os.getenv('TELEGRAM_TOKEN'),
#                    state_storage=state_storage)
#
# from . import auth, awards, common, set_datetime
