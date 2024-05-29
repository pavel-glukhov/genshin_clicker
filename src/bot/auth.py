import logging

from telebot import types
from telebot.asyncio_handler_backends import State, StatesGroup
from src.bot import bot
from src.bot.awards import get_award
from src.bot.keyboards import create_reply_keyboard_buttons
from src.parser.exceptions import CredentialsError
from src.parser.parser import ParserClient
from src.store.scheduler import create_task, scheduler
from src.store.sessions import is_session_exists

logger = logging.getLogger(__name__)


class CredentialsStates(StatesGroup):
    username = State()
    password = State()


@bot.message_handler(func=lambda message: message.text == "Авторизоваться ➡️")
@bot.message_handler(commands=['login'])
async def start_login(message: types.Message):
    chat_id = message.chat.id
    if is_session_exists(chat_id):
        if not scheduler.get_job(str(chat_id)):
            create_task(chat_id=message.chat.id,
                        task_func=get_award)
        
        await bot.send_message(chat_id=chat_id,
                         text='Вы уже авторизованы',
                         reply_markup=create_reply_keyboard_buttons(message))
        return None
    
    await bot.set_state(
        message.from_user.id, CredentialsStates.username, message.chat.id)
    await bot.send_message(
        chat_id=message.chat.id,
        text='Твой юзернейм:')


@bot.message_handler(state=CredentialsStates.username)
async def name_password(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='Твой пароль:')
    await bot.set_state(message.from_user.id, CredentialsStates.password, message.chat.id)
    
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['username'] = message.text


@bot.message_handler(state=CredentialsStates.password)
async def result(message: types.Message):
    async with bot.retrieve_data(
            message.from_user.id, message.chat.id) as data:
        data['password'] = message.text
    
    await bot.send_message(chat_id=message.chat.id,
                     text='Запрос отправлен, '
                          'процесс может занять около 15 секунд.')
    
    client = ParserClient()
    try:
        client.authentication(username=data['username'],
                              password=data['password'], chat_id=message.chat.id)
        
        if client.get_driver.get_cookie('ltoken_v2'):
            markup = create_reply_keyboard_buttons(message)
            await bot.send_message(chat_id=message.chat.id,
                             text='Успешный вход, получение наград запущено.',
                             reply_markup=markup)
            
            if not get_award(message.chat.id):
                await bot.send_message('У вас сегодня нет активных отметок.')
    
    except CredentialsError as ex:
        await bot.send_message(chat_id=message.chat.id,
                         text=ex.__str__())
    finally:
        await bot.delete_state(message.from_user.id, message.chat.id)
        client.get_driver.quit()
