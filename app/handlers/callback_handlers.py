import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.services.user_service import get_or_create_user
from app.services.file_service import get_user_files, get_user_files_count
from app.keyboards import (
    main_menu_keyboard,
    back_to_menu_keyboard,
    files_pagination_keyboard,
    files_list_keyboard,
)
from app.models import File, User

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "menu_back")
async def menu_back_handler(callback: CallbackQuery):
    """Handle back to menu button"""
    await callback.message.edit_text("Main Menu:", reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu_upload")
async def menu_upload_handler(callback: CallbackQuery):
    """Handle upload button - provide clear instructions"""
    upload_instructions = (
        "📤 <b>How to upload a file:</b>\n\n"
        "1. Click the 📎 <b>paperclip</b> icon below\n"
        "2. Choose <b>File</b> or <b>Photo</b>\n"
        "3. Select the file you want to upload\n"
        "4. I'll automatically save it for you!\n\n"
        "You can also just drag and drop any file into this chat."
    )

    await callback.message.edit_text(
        upload_instructions,
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_my_files")
async def menu_my_files_handler(callback: CallbackQuery, session: AsyncSession):
    """Handle my files button - show first page"""
    logger.info(f"User {callback.from_user.id} clicked My Files")
    await show_files_page(callback, session, page=1)


@router.callback_query(F.data.startswith("files_page_"))
async def files_page_handler(callback: CallbackQuery, session: AsyncSession):
    """Handle pagination buttons"""
    try:
        page = int(callback.data.replace("files_page_", ""))
        await show_files_page(callback, session, page)
    except ValueError:
        await callback.answer("Invalid page number.", show_alert=True)

async def show_files_page(callback: CallbackQuery, session: AsyncSession, page: int, limit: int = 10):
    """Show a specific page of user's files"""
    from app.services.file_service import get_user_files, get_user_files_count
    from app.keyboards import files_pagination_keyboard, files_list_keyboard
    
    db_user = await get_or_create_user(session, callback.from_user)
    
    offset = (page - 1) * limit
    
    files = await get_user_files(session, db_user.id, offset=offset, limit=limit)
    total_files = await get_user_files_count(session, db_user.id)
    total_pages = (total_files + limit - 1) // limit  
    
    if not files:
        if page > 1:
            await callback.answer("No more files to show.", show_alert=True)
            return
        
        await callback.message.edit_text(
            "📭 <b>Your storage is empty!</b>\n\n"
            "Send me any file (document, photo, video, audio) and I'll save it for you!\n\n"
            "Click the 📎 paperclip icon below to get started.",
            reply_markup=back_to_menu_keyboard(),
        )
        return
    
    if page < 1 or page > total_pages:
        await callback.answer("Invalid page number.", show_alert=True)
        return
    
    message_text = files_list_keyboard(files, page, total_pages, total_files, offset)
    keyboard = files_pagination_keyboard(files, page, total_pages, offset)
    
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data == "menu_profile")
async def menu_profile_handler(callback: CallbackQuery, session: AsyncSession):
    """Handle profile button"""
    result = await session.execute(
        select(User)
        .where(User.telegram_id == callback.from_user.id)
        .options(selectinload(User.files))
    )
    db_user = result.scalar_one_or_none()

    if not db_user:
        await callback.answer("User not found.", show_alert=True)
        return

    profile_text = (
        f"👤 Your Profile\n\n"
        f"Telegram ID: {db_user.telegram_id}\n"
        f"Username: @{db_user.username or 'N/A'}\n"
        f"Name: {db_user.first_name or ''} {db_user.last_name or ''}\n"
        f"Files Stored: {len(db_user.files)}"
    )

    await callback.message.edit_text(profile_text, reply_markup=back_to_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu_help")
async def menu_help_handler(callback: CallbackQuery):
    """Handle help button"""
    help_text = (
        "ℹ️ Help\n\n"
        "• Just send me any file to save it.\n"
        "• Use 'My Files' to see your list and download anything.\n"
        "• I use Telegram's secure storage, so your files are safe."
    )
    await callback.message.edit_text(help_text, reply_markup=back_to_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("file_get_"))
async def get_file_handler(callback: CallbackQuery, session: AsyncSession):
    """Handle file download button from pagination"""
    file_unique_id = callback.data.replace("file_get_", "")
    
    await callback.answer("Fetching your file...")
    
 
    from sqlalchemy.orm import selectinload
    result = await session.execute(
        select(File)
        .where(File.unique_id == file_unique_id)
        .options(selectinload(File.user)) 
    )
    file_to_send = result.scalar_one_or_none()

    if not file_to_send:
        await callback.answer("❌ File not found.", show_alert=True)
        return

    if file_to_send.user.telegram_id != callback.from_user.id:
        await callback.answer("❌ You don't have permission to access this file.", show_alert=True)
        return

    try:
  
        await callback.message.bot.send_document(
            chat_id=callback.from_user.id,
            document=file_to_send.telegram_file_id,
            caption=f"📁 <b>{file_to_send.name}</b>\n\nID: <code>{file_to_send.unique_id}</code>"
        )
 
        await callback.answer("✅ File sent successfully!")
        
    except Exception as e:
        logger.error(f"Failed to send file: {e}")
        await callback.answer("❌ Sorry, couldn't send the file. It may have expired.", show_alert=True)
