from aiogram.types import ChatPermissions

from app.src.google_sheets.google_spreadsheets import ServiceAccount
from app.src.utils import SERVICE_ACCOUNT_CREDENTIALS, SCOPES
from app.src.config import SPREADSHEET_ID, GROUP_CHAT_ID


sa = ServiceAccount(SERVICE_ACCOUNT_CREDENTIALS, SCOPES, 'sheets', 'v4')

restricted_cache = set()


async def check_restricted_users():
    """
    Background check of restricted users every 5 seconds.
    If a user is added to restricted, he will be restricted in the group.
    If removed from restricted, restrictions will be removed.
    """
    global restricted_cache

    from app.src.tgbot.loader import bot

    try:
        current_restricted = sa.get_restricted_user_ids(SPREADSHEET_ID)
        print(current_restricted)
        to_restrict = current_restricted - restricted_cache
        for user_id in to_restrict:
            try:
                await bot.restrict_chat_member(
                    chat_id=GROUP_CHAT_ID,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                print(f"[+] Restricted: {user_id}")
            except Exception as e:
                print(f"[!] Error in restricting {user_id}: {e}")

        to_unrestrict = restricted_cache - current_restricted
        for user_id in to_unrestrict:
            try:
                await bot.restrict_chat_member(
                    chat_id=GROUP_CHAT_ID,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=True)
                )
                print(f"[-] The restriction has been lifted: {user_id}")
            except Exception as e:
                print(f"[!] Error removing restriction {user_id}: {e}")

        restricted_cache = current_restricted

    except Exception as e:
        print(f"[!] General restricted user verification error: {e}")
