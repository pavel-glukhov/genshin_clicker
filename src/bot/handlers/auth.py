import logging
from typing import Any, Dict

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from concurrent.futures import ThreadPoolExecutor

from src.bot.handlers.awards import get_award
from src.bot.states.auth import AuthState
from src.bot.store.keyboards import create_reply_keyboard_buttons
from src.parser.exceptions import CredentialsError
from src.parser.parser import ParserClient
from src.store.scheduler import create_task
from src.store.sessions import is_session_exists

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command(commands=["login"]))
@router.message(F.text.lower() == "авторизоваться ➡️")
async def start_login(message: Message, state: FSMContext):
    if is_session_exists(message.chat.id):
        await message.answer(
            text="Вы уже авторизованы",
        )
        return None
    
    await state.set_state(AuthState.username)
    await message.answer(text="Логин:")


@router.message(AuthState.username)
async def process_login(message: Message, state: FSMContext) -> None:
    await state.update_data(username=message.text)
    await state.set_state(AuthState.password)
    await message.answer("Твой пароль:")


@router.message(AuthState.password)
async def process_login(message: Message, state: FSMContext) -> None:
    data = await state.update_data(password=message.text)
    await state.clear()
    await message.answer("Запрос на авторизацию отправлен. Процесс может занять до 15 сек.")
    await result(message=message, data=data)


async def result(message: Message, data: Dict[str, Any]) -> None:
    username = data.get('username')
    password = data.get('password')
    chat_id = message.chat.id
    with ThreadPoolExecutor() as executor:
        future = executor.submit(_auth_process, ParserClient, username, password, chat_id)
        auth_result, result_message = future.result()
    
    if auth_result:
        markup = create_reply_keyboard_buttons(message)
        await message.answer(text=result_message,
                             reply_markup=markup)
        create_task(chat_id=chat_id,
                    task_func=get_award)


def _auth_process(client, username, password, chat_id):
    wd_client = client()
    auth_result, result_message = wd_client.authentication(username=username,
                                                           password=password,
                                                           chat_id=chat_id)
    
    wd_client.get_driver.quit()
    return auth_result, result_message
