from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import get_or_create_user
from app.keyboards import main_menu_keyboard
from aiogram.utils.markdown import hbold

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message, session: AsyncSession):
    """Handle /start command"""
    db_user = await get_or_create_user(session, message.from_user)

    welcome_text = (
        f"👋 Hello {hbold(db_user.first_name)}!\n\n"
        f"Welcome to your personal file library. What would you like to do?"
    )
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())


@router.message(Command("menu"))
async def command_menu_handler(message: Message):
    """Handle /menu command"""
    await message.answer("Main Menu:", reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def command_help_handler(message: Message):
    """Handle /help command"""
    help_text = (
        f"{hbold('File Keeper Bot Help')}\n\n"
        "• Just send me any file (document, photo, etc.) to save it\n"
        "• Use 'My Files' to see your uploaded files\n"
        "• Click 'Download' to get any file back instantly\n"
        "• I use Telegram's secure storage - your files are safe!"
    )
    await message.answer(help_text)
