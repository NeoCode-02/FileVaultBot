from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.user_service import get_or_create_user
from app.services.category_service import (
    get_user_categories,
    get_or_create_category,
    set_user_current_category,
    get_user_current_category,
)
from app.keyboards import (
    category_management_keyboard,
    categories_list_keyboard,
    back_to_menu_keyboard,
)
from app.models import Category
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "menu_upload")
async def menu_upload_handler(callback: CallbackQuery, session: AsyncSession):
    """Handle upload button - show category management"""
    db_user = await get_or_create_user(session, callback.from_user)
    current_category = await get_user_current_category(session, db_user.id)

    category_info = ""
    if current_category:
        category_info = f"📂 <b>Current Category:</b> {current_category.name}\n\n"

    upload_instructions = (
        f"{category_info}"
        f"📤 <b>How to upload:</b>\n\n"
        f"1. Choose a category below\n"
        f"2. Click the 📎 <b>paperclip</b> icon\n"
        f"3. Select your file\n"
        f"4. I'll save it to your chosen category!\n\n"
        f"You can also drag and drop files into this chat."
    )

    await callback.message.edit_text(
        upload_instructions,
        reply_markup=category_management_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "switch_category")
async def switch_category_handler(callback: CallbackQuery, session: AsyncSession):
    """Show list of categories to switch to"""
    db_user = await get_or_create_user(session, callback.from_user)
    categories = await get_user_categories(session, db_user.id)
    current_category = await get_user_current_category(session, db_user.id)

    if not categories:
        await callback.message.edit_text(
            "You don't have any categories yet! Create your first one to get started.",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    await callback.message.edit_text(
        "📂 <b>Your Categories:</b>\n\nSelect a category to make it current for uploads:",
        reply_markup=categories_list_keyboard(
            categories, current_category.id if current_category else None
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("select_category_"))
async def select_category_handler(callback: CallbackQuery, session: AsyncSession):
    """Handle category selection"""
    category_id = int(callback.data.replace("select_category_", ""))
    db_user = await get_or_create_user(session, callback.from_user)

    await set_user_current_category(session, db_user.id, category_id)

    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one()

    await callback.message.edit_text(
        f"✅ <b>Category changed!</b>\n\n"
        f"All new uploads will be saved to: <b>{category.name}</b>\n\n"
        f"Now you can send me any file!",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "create_category")
async def create_category_handler(callback: CallbackQuery):
    """Prompt user to create a new category"""
    await callback.message.edit_text(
        "📝 <b>Create New Category</b>\n\n"
        "Please send me the name for your new category.\n\n"
        "Example: <code>Work Documents</code> or <code>Vacation Photos</code>",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.message(F.text & ~F.command)
async def handle_category_name(message: Message, session: AsyncSession):
    """Handle category name input"""
    if len(message.text) > 2 and len(message.text) < 50:
        db_user = await get_or_create_user(session, message.from_user)

        category = await get_or_create_category(session, message.text, db_user.id)
        await set_user_current_category(session, db_user.id, category.id)

        await message.answer(
            f"🎉 <b>Category created!</b>\n\n"
            f"Your new category <b>'{category.name}'</b> is ready!\n\n"
            f"All new uploads will be saved here. Send me a file to get started!",
            reply_markup=back_to_menu_keyboard(),
        )
    else:
        await message.answer(
            "Please provide a valid category name (3-50 characters).",
            reply_markup=back_to_menu_keyboard(),
        )
