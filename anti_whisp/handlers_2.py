import logging
import asyncio
from aiogram import Router
from aiogram.types import Message

logging.basicConfig(level=logging.DEBUG)
router = Router()

@router.message(lambda message: message.text and '🔒' in message.text)
async def deleted_whisper(message: Message):
    await message.delete()
