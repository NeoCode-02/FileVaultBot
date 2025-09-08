from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from decouple import config

from app.middlewares import DbSessionMiddleware
from app.handlers import user_commands, file_handlers, callback_handlers, file_commands

def create_bot() -> Bot:
    """Create and configure bot instance"""
    return Bot(
        token=config('BOT_TOKEN'),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher with all handlers and middleware"""
    dp = Dispatcher()
    
    dp.include_router(user_commands.router)
    dp.include_router(file_handlers.router)
    dp.include_router(callback_handlers.router)
    dp.include_router(file_commands.router) 
    
    dp.update.middleware(DbSessionMiddleware())
    
    return dp

async def start_bot():
    """Start the bot"""
    bot = create_bot()
    dp = create_dispatcher()
    
    await dp.start_polling(bot)