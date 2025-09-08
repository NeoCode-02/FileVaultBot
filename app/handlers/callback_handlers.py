from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton  
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.user_service import get_or_create_user
from app.services.file_service import get_user_files
from app.keyboards import main_menu_keyboard, back_to_menu_keyboard
from app.models import File, User, Category
from aiogram.utils.markdown import hbold

router = Router()

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
    """Handle my files button"""
    db_user = await get_or_create_user(session, callback.from_user)
    files = await get_user_files(session, db_user.id)

    if not files:
        await callback.message.edit_text(
            "Your storage is empty! 📭\n\nSend me your first file and I'll keep it safe for you.",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    builder = InlineKeyboardBuilder()
    
    for file in files:
        button_text = file.name
        if len(button_text) > 20:
            button_text = button_text[:17] + "..."
        
        builder.row(InlineKeyboardButton(
            text=f"📥 {button_text}",
            callback_data=f"file_get_{file.unique_id}"
        ))
    
    builder.row(InlineKeyboardButton(
        text="« Back to Menu",
        callback_data="menu_back"
    ))

    file_list = "\n".join([f"• {file.name} (ID: <code>{file.unique_id}</code>)" for file in files])
    
    await callback.message.edit_text(
        f"📁 <b>Your Files:</b>\n\n{file_list}\n\n"
        f"🔹 <b>Click a button below to download</b>\n"
        f"🔹 Or use: <code>/get {files[0].unique_id if files else 'file_id'}</code>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()

@router.callback_query(F.data == "menu_profile")
async def menu_profile_handler(callback: CallbackQuery, session: AsyncSession):
    """Handle profile button"""
    from sqlalchemy.orm import selectinload
    
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
    """Handle file download button"""
    file_unique_id = callback.data.replace("file_get_", "")
    
    await callback.answer("Fetching your file...")
    
    from sqlalchemy import select
    result = await session.execute(
        select(File).where(File.unique_id == file_unique_id)
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
            caption=f"📁 Here is your file: {file_to_send.name}"
        )
        await callback.message.answer("✅ File sent successfully!")
        
    except Exception as e:
        logger.error(f"Failed to send file: {e}")
        await callback.answer("❌ Sorry, couldn't send the file. It may have expired.", show_alert=True)