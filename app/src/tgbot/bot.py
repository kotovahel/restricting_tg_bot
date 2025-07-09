import logging
from aiogram import Dispatcher

from .loader import bot
from .handlers import register_handlers


async def run_bot():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    register_handlers(dp)
    await dp.start_polling(bot)
