from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.types import Message
from src.store.sessions import is_session_exists


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any]
    ) -> Any:
        
        if not is_session_exists(event.from_user.id):
            await event.answer(("Вы не авторизованы.\n "
                                "Для продолжения,"
                                "выполните команду /login "
                                "и авторизуйтесь под своими учетными данными"))
        else:
            return await handler(event, data)
