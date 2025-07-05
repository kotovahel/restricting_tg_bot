# import os
import asyncio
from tgbot.bot import run_bot
from app.src.checkers.restricted import check_restricted_users


# os.chdir(os.path.dirname(os.path.abspath(__file__)))


async def periodic_check():
    """
    Check restricted users every 5 seconds
    """
    while True:
        await check_restricted_users()
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

