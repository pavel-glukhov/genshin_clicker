import datetime
import logging
import re

from telebot import types
from telebot.asyncio_handler_backends import State, StatesGroup

from src.bot import bot
from src.bot.keyboards import create_reply_keyboard_buttons
from src.store.scheduler import update_task
from src.store.sessions import is_session_exists

logger = logging.getLogger(__name__)


class DateTimeStates(StatesGroup):
    datetime = State()


@bot.message_handler(func=lambda message: message.text == "Указать время ➡️")
@bot.message_handler(commands=['set_time'])
async def update_datetime(message: types.Message):
    chat_id = message.chat.id
    if is_session_exists(chat_id):
        await bot.set_state(
            message.from_user.id, DateTimeStates.datetime, message.chat.id)
        await bot.send_message(
            chat_id=message.chat.id,
            text='Укажи время:\n'
                 'yyyy.mm.dd h:m - год.месяц.день час:минуты\n\n'
                 'Пример: 2023.12.01 12:00')
    else:
        message_text = 'Вы не авторизованы.'
        await bot.send_message(chat_id=message.chat.id,
                         text=message_text,
                         reply_markup=create_reply_keyboard_buttons(message))


@bot.message_handler(state=DateTimeStates.datetime)
async def name_password(message: types.Message):
    new_datetime = _parse_date(message.text)
    update_task(message.chat.id,
                trigger_kwargs={'trigger': 'date',
                                'run_date': new_datetime})
    await bot.send_message(chat_id=message.chat.id, text='Время установлено.')
    await bot.delete_state(message.from_user.id, message.chat.id)


def _parse_date(text):
    time_format_variants = ['%Y,%m,%d,%H,%M', '%Y %m %d %H:%M',
                            '%Y.%m.%d %H:%M', '%Y\\%m\\%d %H:%M',
                            '%Y/%m/%d %H:%M', '%Y %m %d %H %M']
    
    pattern = (r'\d{4}[\s.,/\\]?\d{1,2}[\s.,/\\]?\d{1,2}'
               r'[\s.,/\\]?\d{1,2}[\s.,:/]?\d{1,2}')
    matches = re.findall(pattern, text)
    
    if matches:
        for time_str in matches:
            for fmt in time_format_variants:
                try:
                    date_time = datetime.datetime.strptime(time_str, fmt)
                    return date_time
                
                except ValueError:
                    pass
    
    return False