from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import checkers.keybords as kb

router = Router()

class GameState(StatesGroup):
    Playing = State()

class CheckersGame(StatesGroup):
    WaitingForMove = State()  # Очікування вибору шашки
    WaitingForDestination = State()  # Очікування вибору клітинки для переміщення


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.reply('Hello! Lets play. White move', reply_markup=kb.checkers_board)
    await state.set_state(GameState.Playing)

from aiogram.filters import StateFilter

