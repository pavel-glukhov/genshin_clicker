import logging
from datetime import datetime, timedelta
from random import randint

from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.config import load_config
from src.parser.parser import ParserClient
from src.store.scheduler import create_task, scheduler, update_task
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command(commands=["get_award"]))
@router.message(F.text.lower() == "получить награду 🏆")
async def request_award(message: Message, state: FSMContext):
    await message.answer('Запрос на получение сегодняшней награды запущен. '
                         'Процесс может занять около 15 секунд.')
    
    if not await get_award(message.chat.id):
        await message.answer('У вас сегодня нет активных отметок.')


async def get_award(chat_id: int):
    config = load_config()
    bot = Bot(config.token)
    
    with ThreadPoolExecutor() as executor:
        future = executor.submit(_get_award_process, ParserClient, chat_id)
        data = future.result()
    
    if data.get('daily_award_result'):
        await bot.send_photo(chat_id=chat_id,
                             photo=data.get('daily_award_data').get('img'),
                             caption=data.get('daily_award_data').get('text'))
        if data.get('next_award_result'):
            await bot.send_photo(chat_id=chat_id,
                                 photo=data.get('next_award_data').get('img'),
                                 caption=data.get('next_award_data').get('text'))
        return True
    return False


def _get_award_process(client, chat_id):
    wd_client = client()
    
    logger.info("Getting award")
    wd_client.import_cookies(f'{chat_id}.pkl')
    daily_award_result, daily_award_data = wd_client.get_daily_award()
    next_award_result, next_award_data = wd_client.get_next_award_information()
    
    if scheduler.get_job(str(chat_id)):
        current_datetime = datetime.now()
        time_difference = timedelta(hours=randint(12, 14),
                                    minutes=randint(0, 59))
        new_datetime = current_datetime + time_difference
        update_task(chat_id,
                    trigger_kwargs={'trigger': 'date',
                                    'run_date': new_datetime})
    else:
        create_task(chat_id=chat_id,
                    task_func=get_award)
    wd_client.get_driver.quit()
    logger.info("Driver has been closed.")
    
    return {'daily_award_result': daily_award_result,
            'daily_award_data': daily_award_data,
            'next_award_result': next_award_result,
            'next_award_data': next_award_data}
