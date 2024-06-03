import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.store.scheduler import scheduler

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command(commands=["status"]))
@router.message(F.text.lower() == "статус ℹ️")
async def status(message: Message, state: FSMContext):
    job = scheduler.get_job(str(message.chat.id))
    if job:
        await message.answer(f'Запущен. Следующий запуск '
                             f'{job.next_run_time.strftime("%d %m %Y %H:%M")}')
    else:
        await message.answer(f'Не запущен.')
