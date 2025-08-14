import logging
import random

from aiogram import Router

from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State

import numpy as np

from database import add_player, get_player, update_player

import plants_rpg.keybords as kb


logging.basicConfig(level=logging.DEBUG)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply("Привіт, це рпг про огородника, де тобі треба буде вижити як можна більше, пиши /game щоб почати гру")

@router.message(Command('game'))
async def game_start(message: Message):
    user_id = message.from_user.id
    add_player(user_id)
    await message.reply("Ти починаєш гру з територією 3х3 клітинки, на кожній зараз росте картопля яка виросте через 10 ігрових днів.\n\n"
                        "Натискай кнопку 'Подія' щоб сталась якась подія", reply_markup=kb.event)


event = {'calm weather': '🌤Спокійна, тепла погода. Температура повітря стає temp°C', 'rain': '🌧Починається дощ. Ваші рослини отримують +hum% до вологості',
         'sparrow attack': '🦤Наліт горобців. Вони їдять ваші плоди, ви втратили lost% потенційних плодів, але і 30% шкідників теж померли',
         'heat': '☀️Спека! Температура повітря стає temp°C', 'cold': '🌬Арктичні вітри! Температура повітря знижується до temp°C',
         'pit': '🕳Ви знайшли яму! Ви чітко пам\'ятаєте що раніше її тут не було. Ця клітинка втрачена'}


max_need_humidity = 90 #%
avg_need_humidity = 45

min_need_temperature = 8 #°C
max_need_temperature = 30
avg_need_temperature = 19

def end_game(player):
    player["humidity"] = 45
    player["temperature"] = 19
    player["cell_fruits"] = 10
    player["size_cell"] = np.array([[10, 10, 10], [10, 10, 10], [10, 10, 10]])
    player["fruits"] = 0
    player["day"] = 1
    player["day_humidity"] = 0
    player["day_temperature"] = 0

    update_player(
        player["user_id"],
        humidity=player["humidity"],
        temperature=player["temperature"],
        cell_fruits=player["cell_fruits"],
        size_cell=player["size_cell"],
        fruits=player["fruits"],
        day=player["day"],
        day_humidity=player["day_humidity"],
        day_temperature=player["day_temperature"]
    )

def save_player(player):
    update_player(
        player["user_id"],
        humidity=player["humidity"],
        temperature=player["temperature"],
        cell_fruits=player["cell_fruits"],
        size_cell=player["size_cell"],
        fruits=player["fruits"],
        day=player["day"],
        day_humidity=player["day_humidity"],
        day_temperature=player["day_temperature"]
    )

@router.callback_query(lambda c: c.data == 'pick_event' or c.data == "next_day")
async def start_event(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    player = get_player(user_id)

    if not player:
        add_player(user_id)
        player = get_player(user_id)


    random_event = random.choice(list(event.keys()))

    if random_event == "calm weather":
        temp = random.randint(14, 24)
        text = event[random_event].replace("temp", str(temp))
        player["temperature"] = temp

    elif random_event == 'rain':
        hum = random.randint(10, 30)
        text = event[random_event].replace("hum", str(hum))
        player["humidity"] += hum

    elif random_event == 'sparrow attack':
        lost = random.randint(10, 30)
        text = event[random_event].replace("lost", str(lost))
        if player["temperature"] < avg_need_temperature:
            player["temperature"] += 1
        elif player["temperature"] > avg_need_temperature:
            player["temperature"] -= 1
        player["cell_fruits"] -= player["cell_fruits"] / 100 * lost
        player["cell_fruits"] = round(player["cell_fruits"], 2)

    elif random_event == 'heat':
        temp = random.randint(30, 40)
        text = event[random_event].replace("temp", str(temp))
        player["humidity"] = temp

    elif random_event == "cold":
        temp = random.randint(0, 8)
        text = event[random_event].replace("temp", str(temp))
        player["humidity"] = temp

    elif random_event == 'pit':
        text = event[random_event]
        rows, cols = player["size_cell"].shape
        rand_row = random.randint(0, rows - 1)
        rand_col = random.randint(0, cols - 1)
        player["size_cell"][rand_row, rand_col] = -10

        if player["temperature"] < avg_need_temperature:
            player["temperature"] += 1
        elif player["temperature"] > avg_need_temperature:
            player["temperature"] -= 1
    else:
        text = 'Помилка: Жодної події не знайдено'

    consequences = ''
    if player["humidity"] > max_need_humidity:
        player["size_cell"] += 3
        text += '\n💧Застій води! Занадто велика вологість. Плоди ростимуть на 3 дні довше'
        player["day_humidity"] += 1
    elif player["day_humidity"] > 0 and player["humidity"] > 0:
        player["day_humidity"] = 0
    if player["humidity"] <= 0:
        text += '\n💥Засуха! вологість ґрунту 0%. Плоди ростимуть на 2 дні довше'
        player["size_cell"] += 2
        player["day_humidity"] += 1

    elif player["day_humidity"] > 0 and 0 < player["humidity"] < max_need_humidity:
        player["day_humidity"] = 0

    if player["temperature"] >= max_need_temperature:
        text += '\n☀️Спека! Занадто велика температура повітря. Ви втрачаєте 40% плодів. Вологість втрачається вдвічі швидше'
        player["cell_fruits"] -= player["cell_fruits"] / 100 * 40
        player["cell_fruits"] = round(player["cell_fruits"], 2)
        player["humidity"] -= 10
        player["day_temperature"] += 0

    elif player["day_temperature"] > 0 and player["temperature"] > 0:
        player["day_temperature"] = 0

    if player["temperature"] <= min_need_temperature:
        text += '\n❄️Заморозки! Занадто мала температура повітря. Ви втрачаєте 20% плодів'
        player["cell_fruits"] -= player["cell_fruits"] / 100 * 20
        player["cell_fruits"] = round(player["cell_fruits"], 2)
        player["day_temperature"] += 0

    elif player["day_temperature"] > 0 and 8 < player["temperature"] < player["max_need_temperature"]:
        player["day_temperature"] = 0

    if player["day_temperature"] == 3 or player["day_humidity"] == 3:
        await callback_query.message.edit_text('Ви програли.')
        end_game(player)
        return

    save_player(player)


    await callback_query.message.edit_text(f'{text}.\nПотенційна кількість плодів з клітинки: {player["cell_fruits"]}, вологість дорівнює {player["humidity"]}%, '
                                        f'температура становить {player["temperature"]}°C\n{player["size_cell"]}\n{consequences}\n'
                                        f'Обери покращення для свого городу.', reply_markup=kb.upgrade)

@router.callback_query(lambda c: c.data == 'Expansion')
async def Expansion(callback_query: CallbackQuery):
    await callback_query.answer()

    user_id = callback_query.from_user.id
    player = get_player(user_id)

    if not player:
        add_player(user_id)
        player = get_player(user_id)

    player["size_cell"] -= 1

    if np.any(player["size_cell"] == 0):
        player["fruits"] = player["cell_fruits"] * player["size_cell"].size
        round(player["fruits"], 0)
        player["size_cell"][player["size_cell"] == 0] = 10
    rand_num = random.randint(1, 40)
    if rand_num == 1 or rand_num == 2:
        app = '🕳Під час викопування ямок ви провалились в печеру. Ви втрачаєте один день намагаючись вибратись з неї. Ця клітинка втрачена'
        new_row = np.array([[10, 10, -10]])
        player["humidity"] -= 10
        player["size_cell"] += 1
    elif rand_num == 3:
        app = '🪨Ви розумієте що на цій території багато каміння. Культури будуть рости довше'
        new_row = np.array([[15, 15, 15]])
    else:
        new_row = np.array([[10, 10, 10]])
        app = ''


    player["size_cell"] = np.vstack([player["size_cell"], new_row])
    player["humidity"] -= 10

    player["day"] += 1

    save_player(player)

    await callback_query.message.edit_text(f'{app}\n'
                                           f'Твій город збільшено до \n{player["size_cell"]}\n'
                                        f'День {player["day"]} закінчено, вологість ґрунту становить {player["humidity"]}%, '
                                        f'температура {player["temperature"]}°C, з кожної клітинки вийде {player["cell_fruits"]} плодів. '
                                           f'Ваша кількість плодів: {player["fruits"]}.\n'
                                           f'Очки смерті через температуру: {player["day_temperature"]}. '
                                           f'Очки смерті через вологість: {player["day_humidity"]}', reply_markup=kb.next_day)

@router.callback_query(lambda c: c.data == 'Fertilization')
async def Fertilization(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    player = get_player(user_id)

    if not player:
        add_player(user_id)
        player = get_player(user_id)

    player["size_cell"] -= 1
    if np.any(player["size_cell"] == 0):
        player["fruits"] = player["cell_fruits"] * player["size_cell"].size
        round(player["fruits"], 0)
        player["size_cell"][player["size_cell"] == 0] = 10
    player["cell_fruits"] += 1
    player["cell_fruits"] = round(player["cell_fruits"])
    player["humidity"] -= 10

    player["day"] += 1

    save_player(player)

    await callback_query.message.edit_text(f'Ти удобрив огород. Тепер з кожної клітинки вийде {player["cell_fruits"]} плодів.\n'
                                        f'День {player["day"]} закінчено, вологість ґрунту становить {player["humidity"]}%, '
                                        f'температура {player["temperature"]}°C, ваша кількість плодів: {player["fruits"]}, '
                                           f'розмір городу становить \n{player["size_cell"]}.\n'
                                           f'Очки смерті через температуру: {player["day_temperature"]}. '
                                           f'Очки смерті через вологість: {player["day_humidity"]}', reply_markup=kb.next_day)

@router.callback_query(lambda c: c.data == 'Watering')
async def Watering(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    player = get_player(user_id)

    if not player:
        add_player(user_id)
        player = get_player(user_id)

    player["size_cell"] -= 1
    if np.any(player["size_cell"] == 0):
        player["fruits"] = player["cell_fruits"] * player["size_cell"].size
        round(player["fruits"], 0)
        player["size_cell"][player["size_cell"] == 0] = 10
    player["humidity"] += 30
    player["humidity"] -= 10

    player["day"] += 1

    save_player(player)

    await callback_query.message.edit_text(f'Ти полив огород. Тепер вологість ґрунту становить {player["humidity"]}%.\n'
                                        f'День {player["day"]} закінчено, '
                                        f'температура становить {player["temperature"]}°C, з кожної клітинки вийде {player["cell_fruits"]} плодів,'
                                           f' розмір городу: \n{player["size_cell"]}.\n'
                                           f'Очки смерті через температуру: {player["day_temperature"]}. '
                                           f'Очки смерті через вологість: {player["day_humidity"]}',
                                           reply_markup=kb.next_day)

