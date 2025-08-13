import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import TOKEN
from app.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('aiogram')
logger.setLevel(logging.INFO)


bot = Bot(token = TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")    