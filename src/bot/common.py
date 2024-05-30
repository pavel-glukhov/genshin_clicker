import logging
from pathlib import Path

from telebot import types

from src.bot import bot
from src.bot.keyboards import create_reply_keyboard_buttons
from src.store.scheduler import scheduler
from src.store.sessions import is_session_exists

logger = logging.getLogger(__name__)


@bot.message_handler(state="*", commands=['cancel'])
async def any_state(message: types.Message):
    await bot.send_message(
        message.chat.id, "Отменено.")
    bot.delete_state(
        message.from_user.id, message.chat.id)


@bot.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = create_reply_keyboard_buttons(message)
    
    if is_session_exists(message.chat.id):
        text_message = 'Вы авторизованы. Для удаления вашей сессии, нажмите "Отключить ❌"'
    else:
        text_message = 'Авторизуйтесь для получения ежедневных наград Genshin Impact.'
    
    await bot.send_message(chat_id=message.chat.id,
                           text=text_message,
                           reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Отключить ❌")
@bot.message_handler(commands=['sign_out'])
async def request_award(message: types.Message):
    chat_id = message.chat.id
    session_path = Path(f'sessions\\{chat_id}.pkl')
    if is_session_exists(chat_id):
        session_path.unlink()
        scheduler.remove_job(str(message.chat.id))
        message_text = 'Сессия удалена.'
    else:
        message_text = 'Вы не авторизованы.'
    
    await bot.send_message(chat_id=message.chat.id,
                           text=message_text,
                           reply_markup=create_reply_keyboard_buttons(message))


@bot.message_handler(func=lambda message: message.text == "Статус ℹ️")
@bot.message_handler(commands=['status'])
async def status(message: types.Message):
    job = scheduler.get_job(str(message.chat.id))
    if job:
        await bot.send_message(
            message.chat.id,
            f'Запущен. Следующий запуск '
            f'{job.next_run_time.strftime("%d %m %Y %H:%M")}')
    else:
        await bot.send_message(message.chat.id, f'Не запущен.')
