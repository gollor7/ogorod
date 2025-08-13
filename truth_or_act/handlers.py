import logging
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from workout.handlers import result_text

logging.basicConfig(level=logging.DEBUG)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привіт, скиньте файл формату .txt з вашими питаннями, кожне питання повинно починатись з нового рядку.")

@router.message(F.document)
async def handle_txt(message: Message, bot: Bot):
    document = message.document

    if document.mine_type != "text/plain":
        await message.answer("Не той формат файлу.")
        return

    file = await bot.get_file(document.file_id)
    file_data = await bot.download_file(file.file_path)
    text_data = file_data.read().decode("utf-8")
    processed_text = text_data.upper()

@router.message(Command('truth'))
async def truth(message: Message, state: FSMContext):
    await message.reply("")