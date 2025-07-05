from aiogram import Dispatcher, F, types
from aiogram.types import Message
from app.src.config import SPREADSHEET_ID, GROUP_CHAT_ID
from aiogram.filters import Command
from app.src.google_sheets.google_spreadsheets import ServiceAccount
from app.src.utils import SERVICE_ACCOUNT_CREDENTIALS, SCOPES
import re
from pathlib import Path

ALLOWED_USERNAMES_PATH = Path(__file__).resolve().parents[2] / "data" / "allowed_usernames"

sa = ServiceAccount(SERVICE_ACCOUNT_CREDENTIALS, SCOPES, 'sheets', 'v4')


def load_allowed_usernames(path=ALLOWED_USERNAMES_PATH) -> set[str]:
    with open(path, "r", encoding="utf-8") as f:
        return set(line.strip().lstrip("@") for line in f if line.strip())


def register_handlers(dp: Dispatcher):
    # show command list
    @dp.message(Command("help"))
    async def show_help(message: types.Message):
        help_text = (
            "<b>Available commands:</b>\n\n"
            "/get_chatid — Get the chat ID (use command in the group chat!)\n"
            "/delete — Delete a message\n"
            "/restrict — Restrict a user from sending messages\n"
            "/add_admins — Add hidden admin to the trusted list\n"
        )
        await message.reply(help_text, parse_mode="HTML")

    # get chat id by command '/get_chatid' in chat
    @dp.message(Command("get_chatid"))
    async def get_chat_id(message: types.Message):
        chat_id = message.chat.id
        await message.reply(f"Group ID: {chat_id}")

    # delete message by message ID (access for allowed users)
    @dp.message(F.text.startswith("/delete"))
    async def delete_message_by_id(message: Message):
        # check access
        sender_username = message.from_user.username
        if not sender_username or sender_username.lstrip("@") not in load_allowed_usernames():
            await message.reply("⛔ You do not have access to delete message.")
            return
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

    # restrict member by username (access for allowed users)
    @dp.message(F.text.startswith("/restrict"))
    async def restrict_user_by_username(message: types.Message):
        # check access
        sender_username = message.from_user.username
        if not sender_username or sender_username.lstrip("@") not in load_allowed_usernames():
            await message.reply("⛔ You do not have access to user restrictions.")
            return

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

    # add admins username to allowed_usernames
    @dp.message(F.text.startswith("/add_admins"))
    async def add_usernames(message: Message):
        sender_username = message.from_user.username

        if not sender_username or sender_username.lstrip("@") not in load_allowed_usernames():
            await message.reply("⛔ You do not have access to add admins.")
            return

        args_text = message.text[len("/addadmins"):].strip()

        if "\n" in args_text:
            new_usernames = [line.strip().lstrip("@") for line in args_text.splitlines() if line.strip()]
        else:
            new_usernames = [name.strip().lstrip("@") for name in args_text.split() if name.strip()]

        if not new_usernames:
            await message.reply(
                "❗ Please provide usernames line by line or separated by spaces after the command, for example:\n"
                "/addadmins\n@user1\n@user2\n\nor\n\n/addadmins user1 user2"
            )
            return

        existing_usernames = load_allowed_usernames()
        added_count = 0

        with open(ALLOWED_USERNAMES_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        with open(ALLOWED_USERNAMES_PATH, "a", encoding="utf-8") as f:
            if content and not content.endswith("\n"):
                f.write("\n")
            for username in new_usernames:
                if username not in existing_usernames:
                    f.write(username + "\n")
                    added_count += 1

        await message.reply(f"✅ {added_count} admins added.")

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

    # save new users who left comment
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


