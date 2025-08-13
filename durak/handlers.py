import random
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import durak.keybords as kb

router = Router()

active_games = {}

cards = ['6♠️', '7♠️', '8♠️', '9♠️', '10♠️', 'J♠️', 'Q♠️', 'K♠️', 'A♠️',
        '6♣️', '7♣️', '8♣️', '9♣️', '10♣️', 'J♣️', 'Q♣️', 'K♣️', 'A♣️',
        '6♥️', '7♥️', '8♥️', '9♥️', '10♥️', 'J♥️', 'Q♥️', 'K♥️', 'A♥️',
        '6♦️', '7♦️', '8♦️', '9♦️', '10♦️', 'J♦️', 'Q♦️', 'K♦️', 'A♦️']

# Гравець створює гру
@router.message(F.chat.type.in_({"private", "group", "supergroup"}) & F.text.startswith("/start_game"))
async def start_game(message: Message):
    chat_id = message.chat.id

    if chat_id in active_games:
        await message.answer("Гра вже створена! Використовуйте /join_game для приєднання.")
        return

    # Ініціалізуємо гру
    active_games[chat_id] = {
        "players": [message.from_user.id],  # Перший гравець
        "current_turn": message.from_user.id,  # Першим ходить гравець, який створив гру
        "hand_1": {},
        "hand_2": {}
    }

    await message.answer("Гра створена! Другий гравець може приєднатись за допомогою команди /join_game.")

# Інший гравець приєднується до гри
@router.message(F.chat.type.in_({"private", "group", "supergroup"}) & F.text.startswith("/join_game"))
async def join_game(message: Message):
    chat_id = message.chat.id

    # Перевіряємо, чи є гра в цьому чаті
    if chat_id not in active_games:
        await message.answer("Спочатку створіть гру за допомогою команди /start_game.")
        return

    game = active_games[chat_id]

    # Перевіряємо, чи не зайняте місце другого гравця
    if len(game["players"]) == 2:
        await message.answer("У грі вже є два гравці.")
        return

    # Додаємо другого гравця
    game["players"].append(message.from_user.id)

    await message.answer(
        "Ви успішно приєдналися до гри! Зараз буде роздано карти. Першим ходить гравець, який створив гру.")

    deck = cards.copy()
    hand_1 = random.sample(deck, k=6)
    for card in hand_1:
        deck.remove(card)
    hand_2 = random.sample(deck, k=6)
    for card in hand_2:
        deck.remove(card)

    game["hand_1"][game["players"][0]] = hand_1
    game["hand_2"][game["players"][1]] = hand_2

    await gra(game, hand_1, message)


async def gra(game, hand_1, message: Message):
    async def first_player_move(message: Message):
        first_player_id = game["players"][0]  # Отримуємо ID першого гравця

        # Перевіряємо, чи цей користувач є першим гравцем
        if message.from_user.id == first_player_id:
            reply_kb = [[KeyboardButton(text=v)] for v in hand_1]  # Формуємо кнопки в стовпчик

            await message.answer(
                "Ходить перший гравець",
                reply_markup=ReplyKeyboardMarkup(keyboard=reply_kb, resize_keyboard=True)
            )
        else:
            await message.answer("Зараз хід першого гравця. Будь ласка, зачекайте.")

    await first_player_move(message)





