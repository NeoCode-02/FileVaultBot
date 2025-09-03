import logging
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, User as TgUser
from aiogram.utils.markdown import hbold
from decouple import config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from app.models import User
from app.database import async_session
from app.middlewares import DbSessionMiddleware

BOT_TOKEN = config("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.update.outer_middleware(DbSessionMiddleware(async_session))


@dp.message(CommandStart())
async def command_start_handler(message: Message, session: AsyncSession) -> None:
    """
    Handles the /start command. Registers a new user or welcomes back an existing one.
    Uses a more friendly and engaging tone.
    """
    tg_user: TgUser = message.from_user
    logger.info(f"User {tg_user.id} initiated /start")

    result = await session.execute(select(User).where(User.telegram_id == tg_user.id))
    db_user: None | User = result.scalar_one_or_none()

    if db_user is None:
        db_user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)

        welcome_message = (
            f"👋 Hello {hbold(tg_user.first_name)}! \n\n"
            f"I'm your File Keeper Bot! 🤖 \n\n"
            f"Here's what I can do for you: \n"
            f"• 📁 Save your files (photos, documents, music, etc.) \n"
            f"• 🗂️ Organize them your way \n"
            f"• 🔍 Retrieve them anytime you need \n\n"
            f"Just send me a file to get started!"
        )
    else:
        welcome_message = (
            f"Welcome back, {hbold(tg_user.first_name)}! 🎉 \n\n"
            f"Ready to store or retrieve more files? \n\n"
            f"Your personal storage is ready and waiting."
        )

    await message.answer(welcome_message)
    logger.info(f"User {tg_user.id} handled successfully. New: {db_user is None}")


@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """Provides a helpful guide to the user."""
    help_text = (
        f"{hbold("Need help? Here's how I work:")} \n\n"
        f"📤 {hbold('To Upload:')} Just send me any file (photo, document, audio, etc.). I'll save it for you! \n\n"
        f"📥 {hbold('To Download:')} Use /my_files to see your list and retrieve anything. \n\n"
        f"🗑️ {hbold('To Delete:')} Not implemented yet, but coming soon! \n\n"
        f"Start by sending me a file now!"
    )
    await message.answer(help_text)


@dp.message(Command("my_files"))
async def command_my_files_handler(message: Message, session: AsyncSession) -> None:
    """Lists the user's uploaded files."""
    tg_user = message.from_user

    result = await session.execute(
        select(User)
        .where(User.telegram_id == tg_user.id)
        .options(selectinload(User.files))
    )
    db_user: None | User = result.scalar_one_or_none()

    if not db_user or not db_user.files:
        await message.answer(
            "Your storage is empty! 📭 \n\n"
            "Send me your first file and I'll keep it safe for you."
        )
        return

    file_list = "\n".join(
        [f"• {file.name} ({file.unique_id})" for file in db_user.files]
    )

    await message.answer(
        f"Here are your files, {hbold(tg_user.first_name)}: \n\n{file_list} \n\n"
    )


@dp.message(F.document | F.photo | F.audio | F.video)
async def handle_file_upload(message: Message, session: AsyncSession):
    """This will handle any file a user sends."""

    await message.answer(
        "👍 Got your file! I see you're trying to upload something. \n\n"
        "The full upload feature is being implemented and will be ready very soon!"
    )
    logger.info(f"User {message.from_user.id} sent a file for processing.")


async def main() -> None:
    """Main function to start the bot."""
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
