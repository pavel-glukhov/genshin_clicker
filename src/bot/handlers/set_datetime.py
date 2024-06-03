import datetime
import logging
import re
from typing import Any, Dict

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.handlers.awards import get_award
from src.bot.states.set_datetime import DateTimeStates
from src.bot.store.keyboards import create_reply_keyboard_buttons
from src.store.scheduler import update_task, scheduler, create_task
from src.store.sessions import is_session_exists

logger = logging.getLogger(__name__)

router = Router()


@router.message(StateFilter(None), Command(commands=["set_datetime"]))
@router.message(F.text.lower() == "указать время ➡️")
async def start_login(message: Message, state: FSMContext):
    chat_id = message.chat.id
    if is_session_exists(chat_id):
        await state.set_state(DateTimeStates.datetime)
        await message.answer('Укажи время:\n'
                             'yyyy.mm.dd h:m - год.месяц.день час:минуты\n\n'
                             'Пример: 2023.12.01 12:00')
    else:
        message_text = 'Вы не авторизованы.'
        await message.answer(
            text=message_text,
            reply_markup=create_reply_keyboard_buttons(message))


@router.message(DateTimeStates.datetime)
async def process_login(message: Message, state: FSMContext) -> None:
    data = await state.update_data(datetime=message.text)
    await state.clear()
    await result(message=message, data=data)


async def result(message: Message, data: Dict[str, Any]):
    new_datetime = _parse_date(data.get('datetime'))
    if scheduler.get_job(str(message.chat.id)):
        update_task(message.chat.id,
                    trigger_kwargs={'trigger': 'date',
                                    'run_date': new_datetime})
    else:
        create_task(chat_id=message.chat.id,
                    task_func=get_award)
    await message.answer('Время установлено.')


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
