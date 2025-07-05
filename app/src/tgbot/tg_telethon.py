from telethon import TelegramClient
from app.src.config import TG_API_ID, TG_API_HASH, USER_PHONE_NUMBER, GROUP_LINK

client = TelegramClient(USER_PHONE_NUMBER, TG_API_ID, TG_API_HASH)


async def get_old_members():
    async with client:
        print("Client started. Fetching group participants...")
        participants = await client.get_participants(GROUP_LINK)

        print(f"Total participants: {len(participants)}")

        users_list = []
        for user in participants:
            users_list.append({
                "id": str(user.id),
                "username": user.username or "",
                "name": user.first_name or ""
            })
            print(user.id, user.username, user.first_name)

        return users_list

