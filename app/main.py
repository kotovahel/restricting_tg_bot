import os

import asyncio

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from src.tgbot.bot import run_bot
from src.restricted import check_restricted_users
from src.tgbot.loader import bot


async def periodic_check():
    """
    Check restricted users every 5 seconds
    """
    while True:
        await check_restricted_users(bot)
        await asyncio.sleep(5)


async def main():
    """
    Run tgbot and users check in parallels
    """
    await asyncio.gather(
        run_bot(),
        periodic_check()
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as ex:
        print(ex)
