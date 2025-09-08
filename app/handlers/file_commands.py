from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import File
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("get"))
async def get_file_command(message: Message, command: CommandObject, session: AsyncSession):
    """Handle /get <file_id> command"""
    if not command.args:
        await message.answer(
            "📝 <b>Usage:</b> /get &lt;file_id&gt;\n\n"
            "Example: <code>/get abc123</code>\n\n"
            "Use <b>My Files</b> to see your file IDs."
        )
        return
    
    file_unique_id = command.args.strip()
    
    logger.info(f"User {message.from_user.id} requested file: {file_unique_id}")
    
    result = await session.execute(
        select(File).where(File.unique_id == file_unique_id)
    )
    file_to_send = result.scalar_one_or_none()

    if not file_to_send:
        await message.answer("❌ File not found. Please check the file ID.")
        return

    if file_to_send.user.telegram_id != message.from_user.id:
        await message.answer("❌ You don't have permission to access this file.")
        return

    try:
        await message.answer_document(
            document=file_to_send.telegram_file_id,
            caption=f"📁 <b>{file_to_send.name}</b>\n\nID: <code>{file_to_send.unique_id}</code>"
        )
        
    except Exception as e:
        logger.error(f"Failed to send file: {e}")
        await message.answer("❌ Sorry, couldn't send the file. It may have expired.")