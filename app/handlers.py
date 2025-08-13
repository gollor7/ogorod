from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import app.keybords as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Привіт.\nТвій ID: {message.from_user.id}\nІм`я: {message.from_user.first_name}', reply_markup = kb.settings)

@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Це /help')

@router.message(F.text == 'Як справи?')
async def how_are_you(message: Message):
    await message.answer('OK!')

@router.message(Command('get_photo'))
async def get_photo(message: Message):
    await message.answer_photo(photo = 'AgACAgIAAxkBAAIB4meOXuhpg2NuWmQ8Nu-B98JmDa5bAAK96TEb6bRwSAM1SeWf-RBOAQADAgADeAADNgQ', caption = "Кросівоє")

@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f'ID фото: {message.photo[-1].file_id}')