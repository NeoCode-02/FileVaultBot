from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db_session

class DbSessionMiddleware(BaseMiddleware):
    """Middleware to inject database session into handler data"""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async for session in get_db_session():
            data["session"] = session
            return await handler(event, data)
