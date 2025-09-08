from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import get_or_create_user
from app.services.file_service import get_general_category, create_file_record
from app.services.category_service import get_user_current_category
from app.keyboards import main_menu_keyboard
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.document | F.photo | F.video | F.audio)
async def handle_file_message(message: Message, session: AsyncSession):
    """Handle all file uploads with category support"""
    db_user = await get_or_create_user(session, message.from_user)
    current_category = await get_user_current_category(session, db_user.id)

    if not current_category:
        current_category = await get_general_category(session)

    if message.document:
        file_obj = message.document
    elif message.photo:
        file_obj = message.photo[-1]
    elif message.video:
        file_obj = message.video
    elif message.audio:
        file_obj = message.audio
    else:
        await message.answer("Unsupported file type.")
        return

    file_data = {
        "name": file_obj.file_name or "Unnamed File",
        "mime_type": getattr(file_obj, "mime_type", "unknown/type"),
        "size": file_obj.file_size,
        "telegram_file_id": file_obj.file_id,
    }

    new_file = await create_file_record(
        session, file_data, db_user.id, current_category.id
    )

    success_message = (
        f"✅ <b>File saved successfully!</b>\n\n"
        f"📁 <b>Name:</b> {new_file.name}\n"
        f"📂 <b>Category:</b> {current_category.name}\n"
        f"🆔 <b>ID:</b> <code>{new_file.unique_id}</code>\n\n"
        f"🔹 <b>To download later:</b>\n"
        f"• Click <b>My Files</b> in the menu\n"
        f"• Or use: <code>/get {new_file.unique_id}</code>"
    )
    await message.answer(success_message, reply_markup=main_menu_keyboard())
