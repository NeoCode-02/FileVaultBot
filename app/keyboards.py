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
        inline_keyboard=[
            [InlineKeyboardButton(text="« Back to Menu", callback_data="menu_back")]
        ]
    )


def files_pagination_keyboard(files, current_page: int, total_pages: int, offset: int):
    """Create keyboard for files list with pagination"""
    builder = InlineKeyboardBuilder()

    for i, file in enumerate(files, 1):
        display_number = offset + i
        button_text = f"{display_number}. {file.name}"
        if len(button_text) > 25:
            button_text = button_text[:22] + "..."

        builder.row(
            InlineKeyboardButton(
                text=button_text, callback_data=f"file_get_{file.unique_id}"
            )
        )

    pagination_buttons = []

    if current_page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Previous", callback_data=f"files_page_{current_page - 1}"
            )
        )

    if current_page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Next ➡️", callback_data=f"files_page_{current_page + 1}"
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(InlineKeyboardButton(text="« Back to Menu", callback_data="menu_back"))

    return builder.as_markup()


def files_list_keyboard(
    files, page: int, total_pages: int, total_files: int, offset: int
):
    """Create the complete files list message with pagination info"""
    file_list = ""
    for i, file in enumerate(files, 1):
        display_number = offset + i
        file_list += (
            f"{display_number}. {file.name} (ID: <code>{file.unique_id}</code>)\n"
        )

    message_text = (
        f"📁 <b>Your Files</b> (Page {page}/{total_pages})\n"
        f"📊 Total files: {total_files}\n\n"
        f"{file_list}\n"
        f"🔹 <b>Click a file to download it</b>\n"
        f"🔹 Or use: <code>/get file_id</code>"
    )

    return message_text


def category_management_keyboard():
    """Keyboard for category management"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📁 Create New Category", callback_data="create_category"
        ),
        InlineKeyboardButton(
            text="📂 Switch Category", callback_data="switch_category"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="📤 Upload to Current", callback_data="upload_current"
        ),
        InlineKeyboardButton(
            text="🗑️ Manage Categories", callback_data="manage_categories"
        ),
    )
    builder.row(
        InlineKeyboardButton(text="« Back to Menu", callback_data="menu_back"),
    )
    return builder.as_markup()


def categories_list_keyboard(categories, current_category_id: None | int = None):
    """Keyboard for listing categories"""
    builder = InlineKeyboardBuilder()

    for category in categories:
        prefix = "✅ " if category.id == current_category_id else "📁 "
        builder.row(
            InlineKeyboardButton(
                text=f"{prefix}{category.name}",
                callback_data=f"select_category_{category.id}",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Create New Category", callback_data="create_category"
        )
    )

    builder.row(
        InlineKeyboardButton(text="« Back to Upload", callback_data="menu_upload")
    )

    return builder.as_markup()
