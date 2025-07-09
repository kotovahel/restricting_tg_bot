from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Original keyboard
def build_initial_admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add admins", callback_data="add_admins_prompt")],
            [InlineKeyboardButton(text="🗑️ Delete admin", callback_data="delete_admin_start")],
            [InlineKeyboardButton(text="🗑️ Delete message by ID", callback_data="delete_message_prompt")],
            [InlineKeyboardButton(text="🚫 Restrict user", callback_data="restrict_user_prompt")]
        ]
    )


# Keyboard with users to delete
def build_admin_list_keyboard(usernames, start=0, per_page=5):
    usernames = usernames[::-1]
    total = len(usernames)
    page_usernames = usernames[start:start + per_page]

    keyboard_buttons = []

    # Button with admin usernames
    for username in page_usernames:
        keyboard_buttons.append([
            InlineKeyboardButton(text=f"@{username}", callback_data=f"confirm_delete:{username}")
        ])

    # Navigation buttons
    nav_buttons = []
    if start >= per_page:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"prev_page:{start - per_page}"))
    if total > start + per_page:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data=f"next_page:{start + per_page}"))

    if nav_buttons:
        keyboard_buttons.append(nav_buttons)

    # Cancel button
    keyboard_buttons.append([
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_admin_action")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


# Confirm deletion
def build_confirm_delete_keyboard(username):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes", callback_data=f"delete_confirm_yes:{username}"),
                InlineKeyboardButton(text="❌ No", callback_data=f"delete_confirm_no:{username}")
            ],
            [InlineKeyboardButton(text="🔙 Cancel", callback_data="cancel_admin_action")]
        ]
    )


# Keyboard when adding
def build_add_admin_prompt_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Cancel", callback_data="cancel_admin_action")]
        ]
    )
