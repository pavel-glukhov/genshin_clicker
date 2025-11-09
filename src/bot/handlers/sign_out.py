import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.store.keyboards import create_reply_keyboard_buttons
from src.config import load_config
from src.store.scheduler import scheduler
from src.store.sessions import is_session_exists

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command(commands=["sign_out"]))
@router.message(F.text.lower() == "отключить ❌")
async def sign_out(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    session_path = Path(f'{load_config().sessions_folder}\\{chat_id}.pkl')
    if is_session_exists(chat_id):
        session_path.unlink()
        if scheduler.get_job(str(message.chat.id)):
            scheduler.remove_job(str(message.chat.id))
    
    message_text = '✅ Сессия удалена.'
    
    await message.answer(text=message_text,
                         reply_markup=create_reply_keyboard_buttons(message))
