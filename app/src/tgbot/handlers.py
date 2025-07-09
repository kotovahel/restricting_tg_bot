import re
from pathlib import Path
from functools import wraps

from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.filters import Command
from aiogram import Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import SPREADSHEET_ID, GROUP_CHAT_ID
from src.google_spreadsheets import ServiceAccount
from src.utils import SERVICE_ACCOUNT_CREDENTIALS, SCOPES
from .loader import bot

from .keyboards import (
    build_initial_admin_keyboard,
    build_admin_list_keyboard,
    build_confirm_delete_keyboard,
    build_add_admin_prompt_keyboard,
)

ALLOWED_USERNAMES_PATH = Path(__file__).resolve().parents[2] / "data" / "allowed_usernames"

sa = ServiceAccount(SERVICE_ACCOUNT_CREDENTIALS, SCOPES, 'sheets', 'v4')


def load_allowed_usernames(path=ALLOWED_USERNAMES_PATH) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().lstrip("@") for line in f if line.strip()]


def save_usernames(usernames):
    with open(ALLOWED_USERNAMES_PATH, "w", encoding="utf-8") as f:
        for username in usernames:
            f.write(username.strip().lstrip("@") + "\n")


def is_allowed_user(username: str) -> bool:
    if not username:
        return False
    return username.lstrip("@") in load_allowed_usernames()


def admin_only(handler):
    @wraps(handler)
    async def wrapper(event, *args, **kwargs):
        username = getattr(event.from_user, "username", None)
        if not is_allowed_user(username):
            if isinstance(event, Message):
                await event.reply("⛔ You do not have access.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ You do not have access.", show_alert=True)
            return
        return await handler(event, *args, **kwargs)

    return wrapper


def register_handlers(dp: Dispatcher):
    # show command list
    @dp.message(Command("help"))
    async def show_help(message: types.Message):
        help_text = (
            "<b>Available commands:</b>\n\n"
            "/start — Start the bot communication\n"
            "/get_chatid — Get the chat ID (use command in the group chat!)\n"
            "/delete — Delete a message\n"
            "/restrict — Restrict a user from sending messages\n"
        )
        await message.reply(help_text, parse_mode="HTML")

    @dp.message(Command("get_chatid"))
    async def get_chat_id(message: types.Message):
        chat_id = message.chat.id
        await message.reply(f"Group ID: {chat_id}")

    @dp.message(F.text.startswith("/delete"))
    @admin_only
    async def delete_message_by_id(message: Message):
        match = re.match(r"/delete\s+(\d+)", message.text)
        if not match:
            await message.reply("❗ Please enter the message ID, for example:\n<b>/delete 12345</b>", parse_mode="HTML")
            return
        msg_id = int(match.group(1))
        try:
            await message.bot.delete_message(chat_id=GROUP_CHAT_ID, message_id=msg_id)
            await message.reply(f"✅ Message {msg_id} removed from group.")
        except Exception as e:
            await message.reply(f"❌ Failed to delete message: {e}")

    @dp.message(F.text.startswith("/restrict"))
    @admin_only
    async def restrict_user_by_username(message: types.Message):

        match = re.match(r"/restrict\s+(@?\w+)", message.text)
        if not match:
            await message.reply("❗ Please enter the username, for example:\n<b>/restrict alice123</b>",
                                parse_mode="HTML")
            return

        target_username = match.group(1).lstrip("@")

        try:
            sa.restrict_user(SPREADSHEET_ID, target_username)
            await message.reply(f"✅ User @{target_username} is marked as restricted.")
        except ValueError as ve:
            await message.reply(f"⚠️ {ve}")
        except Exception as e:
            await message.reply(f"❌ Error restricting user: {e}")

    class AddAdmins(StatesGroup):
        waiting_for_usernames = State()

    @dp.message(Command("start"))
    @admin_only
    async def start_command_handler(message: Message):
        await message.answer(
            "👋 Hello! Welcome to the bot.\nClick the button below to open the admin panel.",
            reply_markup=build_initial_admin_keyboard()
        )
        await bot.set_my_commands([
            BotCommand(command="start", description="Start the bot communication"),
            BotCommand(command="help", description="Get commands"),
            BotCommand(command="get_chatid", description="Get the chat ID (use command in the group chat!)"),
            BotCommand(command="delete", description="Delete a message"),
            BotCommand(command="restrict", description="Restrict a user from sending messages"),
        ])

    @dp.message(Command("admin"))
    @admin_only
    async def admin_panel(message: Message):
        await message.reply("🔧 Admin panel:", reply_markup=build_initial_admin_keyboard())

    @dp.callback_query(F.data == "add_admins_prompt")
    @admin_only
    async def prompt_add_admins(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "✏️ Enter usernames to add (one per line or separated by spaces):",
            reply_markup=build_add_admin_prompt_keyboard()
        )
        await state.set_state(AddAdmins.waiting_for_usernames)
        await callback.answer()

    @dp.message(AddAdmins.waiting_for_usernames)
    async def process_add_admins_input(message: Message, state: FSMContext):
        input_text = message.text

        new_usernames_raw = [line.strip().lstrip("@") for line in input_text.splitlines()] if "\n" in input_text \
            else [name.strip().lstrip("@") for name in input_text.split()]
        new_usernames = [name for name in new_usernames_raw if name]

        existing_usernames = load_allowed_usernames()
        existing_usernames_lower = {u.lower() for u in existing_usernames}

        added_count = 0
        with open(ALLOWED_USERNAMES_PATH, "a", encoding="utf-8") as f:
            for username in new_usernames:
                if username.lower() not in existing_usernames_lower:
                    f.write(username.lower() + "\n")
                    added_count += 1

        await message.answer(f"✅ {added_count} admins added.", reply_markup=build_initial_admin_keyboard())
        await state.clear()

    # delete admin username
    @dp.callback_query(F.data == "delete_admin_start")
    @admin_only
    async def show_admins_to_delete(callback: CallbackQuery):

        usernames = list(load_allowed_usernames())

        if not usernames:
            await callback.message.edit_text("❗ No admins to delete.", reply_markup=build_initial_admin_keyboard())
            return

        await callback.message.edit_text(
            "🗑️ Select admin to delete:",
            reply_markup=build_admin_list_keyboard(usernames)
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("next_page:"))
    @admin_only
    async def next_admins_page(callback: CallbackQuery):
        offset = int(callback.data.split(":")[1])
        usernames = list(load_allowed_usernames())
        await callback.message.edit_text("🗑️ Select admin to delete:",
                                         reply_markup=build_admin_list_keyboard(usernames, start=offset))
        await callback.answer()

    @dp.callback_query(F.data.startswith("prev_page:"))
    @admin_only
    async def previous_admins_page(callback: CallbackQuery):

        offset = int(callback.data.split(":")[1])
        usernames = list(load_allowed_usernames())
        await callback.message.edit_text(
            "🗑️ Select admin to delete:",
            reply_markup=build_admin_list_keyboard(usernames, start=offset)
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("confirm_delete:"))
    @admin_only
    async def confirm_delete(callback: CallbackQuery):
        username = callback.data.split(":")[1]
        await callback.message.edit_text(f"❔ Delete {username}?", reply_markup=build_confirm_delete_keyboard(username))
        await callback.answer()

    @dp.callback_query(F.data.startswith("delete_confirm_yes:"))
    @admin_only
    async def delete_admin(callback: CallbackQuery):
        username = callback.data.split(":")[1]
        usernames = list(load_allowed_usernames())
        if username in usernames:
            usernames.remove(username)
            save_usernames(usernames)
            await callback.message.edit_text(f"✅ @{username} removed.", reply_markup=build_initial_admin_keyboard())
        else:
            await callback.message.edit_text("⚠️ Username not found.", reply_markup=build_initial_admin_keyboard())
        await callback.answer()

    @dp.callback_query(F.data.startswith("delete_confirm_no:"))
    @admin_only
    async def cancel_delete_admin(callback: CallbackQuery):
        await callback.message.edit_text("❌ Deletion cancelled.", reply_markup=build_initial_admin_keyboard())
        await callback.answer()

    @dp.callback_query(F.data == "cancel_admin_action")
    @admin_only
    async def cancel_action(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text("🔙 Action cancelled.", reply_markup=build_initial_admin_keyboard())
        await state.clear()
        await callback.answer()

    class MessageActions(StatesGroup):
        waiting_for_message_id = State()
        waiting_for_restrict_username = State()

    # delete message
    @dp.callback_query(F.data == "delete_message_prompt")
    @admin_only
    async def prompt_delete_message(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "🆔 Enter the message ID you want to delete:",
            reply_markup=build_add_admin_prompt_keyboard()
        )
        await state.set_state(MessageActions.waiting_for_message_id)
        await callback.answer()

    @dp.message(MessageActions.waiting_for_message_id)
    @admin_only
    async def process_delete_message_id(message: Message, state: FSMContext):

        match = re.match(r"^\d+$", message.text.strip())
        if not match:
            await message.reply("❗ Please enter a valid numeric message ID.")
            return

        msg_id = int(message.text.strip())
        try:
            await message.bot.delete_message(chat_id=GROUP_CHAT_ID, message_id=msg_id)
            await message.reply(f"✅ Message {msg_id} removed from group.", reply_markup=build_initial_admin_keyboard())
        except Exception as e:
            await message.reply(f"❌ Failed to delete message: {e}", reply_markup=build_initial_admin_keyboard())
        await state.clear()

    # restrict users
    @dp.callback_query(F.data == "restrict_user_prompt")
    @admin_only
    async def prompt_restrict_user(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "✏️ Enter the username to restrict (without @):",
            reply_markup=build_add_admin_prompt_keyboard()
        )
        await state.set_state(MessageActions.waiting_for_restrict_username)
        await callback.answer()

    @dp.message(MessageActions.waiting_for_restrict_username)
    @admin_only
    async def process_restrict_username(message: Message, state: FSMContext):

        target_username = message.text.strip().lstrip("@")
        if not target_username.isalnum():
            await message.reply("❗ Please enter a valid username.")
            return

        try:
            sa.restrict_user(SPREADSHEET_ID, target_username)
            await message.reply(f"✅ User @{target_username} is marked as restricted.",
                                reply_markup=build_initial_admin_keyboard())
        except ValueError as ve:
            await message.reply(f"⚠️ {ve}", reply_markup=build_initial_admin_keyboard())
        except Exception as e:
            await message.reply(f"❌ Error restricting user: {e}", reply_markup=build_initial_admin_keyboard())
        await state.clear()

    # save new group members
    @dp.message(F.new_chat_members)
    async def new_members_handler(message: Message):
        for user in message.new_chat_members:
            user_data = {
                "id": user.id,
                "name": user.full_name,
                "username": user.username
            }
            sa.save_user_to_sheets(SPREADSHEET_ID, user_data)
            print(f"🟢 New group member: {user.full_name} (ID: {user.id}, username: @{user.username})")

    # save user by message in group
    @dp.message(F.chat.type.in_({"group", "supergroup"}))
    async def group_message_handler(message: Message):
        user = message.from_user
        user_data = {
            "id": user.id,
            "name": user.full_name,
            "username": user.username
        }
        sa.save_user_to_sheets(SPREADSHEET_ID, user_data)
        print(f"💬 Message in group from {user.full_name} (ID: {user.id}): {message.text}")
