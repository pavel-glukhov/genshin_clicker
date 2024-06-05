import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.store.keyboards import create_reply_keyboard_buttons

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    markup = create_reply_keyboard_buttons(message)
    text_message = ('Вы авторизованы.\n'
                    'Для удаления вашей сессии, нажмите "Отключить ❌"')
    
    await message.answer(text=text_message,
                         reply_markup=markup)
