from telebot import types

from src.store.sessions import is_session_exists


def create_reply_keyboard_buttons(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if not is_session_exists(message.chat.id):
        auth_button = types.KeyboardButton("Авторизоваться ➡️")
        
        markup.add(auth_button)
    else:
        sign_out_button = types.KeyboardButton("Отключить ❌")
        award_button = types.KeyboardButton("Получить награду 🏆")
        status_button = types.KeyboardButton("Статус ℹ️")
        set_datetime = types.KeyboardButton("Указать время ➡️")
        markup.add(award_button, status_button, set_datetime, sign_out_button)
    
    return markup