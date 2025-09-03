from aiogram import BaseMiddleware
from .database import async_session


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory):
        self.session_factory = async_session

    async def __call__(self, handler, event, data):
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)
