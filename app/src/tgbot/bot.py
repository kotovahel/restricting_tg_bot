import logging
from aiogram import Dispatcher
from app.src.tgbot.loader import bot
from app.src.tgbot.handlers import register_handlers


async def run_bot():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    register_handlers(dp)
    await dp.start_polling(bot)