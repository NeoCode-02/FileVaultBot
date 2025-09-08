from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create the main inline menu"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📤 Upload File", callback_data="menu_upload"),
        InlineKeyboardButton(text="📥 My Files", callback_data="menu_my_files"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 Profile", callback_data="menu_profile"),
        InlineKeyboardButton(text="ℹ️ Help", callback_data="menu_help"),
    )
    return builder.as_markup()

def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with only a back button"""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="« Back to Menu", callback_data="menu_back")]]
    )