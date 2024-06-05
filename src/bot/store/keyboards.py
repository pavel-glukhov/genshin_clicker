from aiogram import types

from src.store.sessions import is_session_exists


def create_reply_keyboard_buttons(message: types.Message):
    if not is_session_exists(message.chat.id):
        kb = [
            [types.KeyboardButton(text="Авторизоваться ➡️")],
        ]
    else:
        kb = [
            [types.KeyboardButton(text="Отключить ❌")],
            [types.KeyboardButton(text="Получить награду 🏆")],
            [types.KeyboardButton(text="Статус ℹ️")],
            [types.KeyboardButton(text="Указать время ➡️")],
        ]
    
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb,
                                         resize_keyboard=True,
                                         one_time_keyboard=True)
    
    return keyboard
