import logging

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.store.scheduler import scheduler

logger = logging.getLogger(__name__)

router = Router()


@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    if not state_data:
        await message.answer(
            text="Нечего отменять",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.clear()
        await message.answer(
            text="Действие отменено",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(Command(commands=["status"]))
@router.message(F.text.lower() == "статус ℹ️")
async def status(message: Message, state: FSMContext) -> None:
    job = scheduler.get_job(str(message.chat.id))
    if job:
        await message.answer(f'Запущен. Следующий запуск '
                             f'{job.next_run_time.strftime("%d-%m-%Y %H:%M")}')
    else:
        await message.answer(f'Не запущен.')
