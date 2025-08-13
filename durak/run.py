import asyncio
import logging

from aiogram import Bot, Dispatcher

from durak.config import TOKEN
from durak.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('aiogram')
logger.setLevel(logging.INFO)


bot = Bot(token = TOKEN)
dp = Dispatcher()

async def durak_hand():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(durak_hand())
    except KeyboardInterrupt:
        print("Exit")