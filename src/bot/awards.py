import logging
from datetime import datetime, timedelta
from random import randint

from telebot import types

from src.bot import bot
from src.parser.exceptions import NoAwardsError
from src.parser.parser import ParserClient
from src.store.scheduler import create_task, scheduler, update_task
from src.store.sessions import is_session_exists

logger = logging.getLogger(__name__)


@bot.message_handler(func=lambda message: message.text == "Получить награду 🏆")
@bot.message_handler(commands=['award'])
async def request_award(message: types.Message):
    if is_session_exists(message.chat.id):
        await bot.send_message(
            message.chat.id,
            'Запрос на получение сегодняшней награды запущен. '
            'Процесс может занять около 15 секунд.')
        
        if not get_award(message.chat.id):
            await bot.send_message(message.chat.id, 'У вас сегодня нет активных отметок.')
    else:
        await bot.send_message(
            message.chat.id, 'Вы не авторизованы')


def get_award(chat_id) -> bool:
    result = True
    client = ParserClient()
    try:
        logger.info("Getting award")
        client.import_cookies(f'{chat_id}.pkl')
        daily_award = client.get_daily_award()
        bot.send_photo(chat_id=chat_id,
                       photo=daily_award.get('img'),
                       caption=daily_award.get('text'))
    except NoAwardsError as e:
        logger.info(f'Chat id: {chat_id} - {e.__str__()}')
        result = False
    try:
        next_award = client.get_next_award_information()
        bot.send_photo(chat_id=chat_id,
                       photo=next_award.get('img'),
                       caption=next_award.get('text'))
    
    except NoAwardsError as e:
        logger.info(f'Chat id: {chat_id} - {e.__str__()}')
    
    finally:
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
        client.get_driver.quit()
    return result
