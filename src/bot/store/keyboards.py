from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from src.store.sessions import is_session_exists


def create_reply_keyboard_buttons(message: Message):
    if not is_session_exists(message.chat.id):
        kb = [
            [KeyboardButton(text="Авторизоваться ➡️")],
        ]
    else:
        kb = [
            [KeyboardButton(text="Получить награду 🏆")],
            [KeyboardButton(text="Статус ℹ️")],
            [KeyboardButton(text="Отключить ❌")],
        ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb,
                                   resize_keyboard=True,
                                   one_time_keyboard=True)

    return keyboard
