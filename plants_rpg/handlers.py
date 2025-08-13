import logging
import random

from aiogram import Router

from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State

import numpy as np

import plants_rpg.keybords as kb


logging.basicConfig(level=logging.DEBUG)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply("Привіт, це рпг про огородника, де тобі треба буде вижити як можна більше, пиши /game щоб почати гру")

@router.message(Command('game'))
async def game_start(message: Message):
    await message.reply("Ти починаєш гру з територією 3х3 клітинки, на кожній зараз росте картопля яка виросте через 10 ігрових днів.\n\n"
                        "Натискай кнопку 'Подія' щоб сталась якась подія", reply_markup=kb.event)


event = {'calm weather': 'Спокійна, тепла погода. Температура повітря стає temp°C', 'rain': 'Починається дощ. Ваші рослини отримують +hum% до вологості',
         'sparrow attack': 'Наліт горобців. Вони їдять ваші плоди, ви втратили lost% потенційних плодів, але і 30% шкідників теж померли',
         'heat': 'Жара! Температура повітря стає temp°C', 'cold': 'Арктичні вітри! Температура повітря знижується до temp°C',
         'pit': 'Ви знайшли яму! Ви чітко пам\'ятаєте що раніше її тут не було. Ця клітинка втрачена'}


max_need_humidity = 90 #%
avg_need_humidity = 45

min_need_temperature = 8 #°C
max_need_temperature = 30
avg_need_temperature = 19

cell_fruits = 10

growth_days = 10

size_cell = np.array([[10, 10, 10],
              [10, 10, 10],
              [10, 10, 10]])

humidity = 45

temperature = 19

fruits = 0

@router.callback_query(lambda c: c.data == 'pick_event' or c.data == "next_day")
async def start_event(callback_query: CallbackQuery):
    await callback_query.answer()
    random_event = random.choice(list(event.keys()))
    global humidity
    global temperature
    global cell_fruits
    global size_cell

    if random_event == "calm weather":
        temp = random.randint(14, 24)
        text = event[random_event].replace("temp", str(temp))
        temperature = temp

    elif random_event == 'rain':
        hum = random.randint(10, 30)
        text = event[random_event].replace("hum", str(hum))
        humidity += hum

    elif random_event == 'sparrow attack':
        lost = random.randint(10, 30)
        text = event[random_event].replace("lost", str(lost))
        if temperature < avg_need_temperature:
            temperature += 1
        elif temperature > avg_need_temperature:
            temperature -= 1
        cell_fruits -= cell_fruits / 100 * lost
        cell_fruits = round(cell_fruits, 2)
    elif random_event == 'heat':
        temp = random.randint(30, 40)
        text = event[random_event].replace("temp", str(temp))
    elif random_event == "cold":
        temp = random.randint(0, 8)
        text = event[random_event].replace("temp", str(temp))
    elif random_event == 'pit':
        text = event[random_event]
        rows, cols = size_cell.shape
        rand_row = random.randint(0, rows - 1)
        rand_col = random.randint(0, cols - 1)
        size_cell[rand_row, rand_col] = "A"
    else:
        text = 'Помилка: Жодної події не знайдено'

    global size_cell
    if humidity > max_need_humidity:
        size_cell += 3
        consequences = 'Застій води! Занадто велика вологість. Плоди ростимуть на 3 дні довше'
    elif humidity == 0:
        consequences = 'Засуха! вологість ґрунту 0%. Плоди ростимуть на 2 дні довше'
        size_cell += 2
    elif temperature >= max_need_temperature:
        consequences = 'Спека! Занадто велика температура повітря. Ви втрачаєте 40% плодів. Вологість втрачається вдвічі швидше'
        cell_fruits -= cell_fruits / 100 * 40
        cell_fruits = round(cell_fruits, 2)
        humidity -= 10
    elif temperature <= min_need_temperature:
        consequences = 'Заморозки! Занадто мала температура повітря. Ви втрачаєте 20% плодів'
        cell_fruits -= cell_fruits / 100 * 20
        cell_fruits = round(cell_fruits, 2)
    else:
        consequences = ''





    await callback_query.message.answer(f'{text}.\nПотенційна кількість плодів з клітинки: {cell_fruits}, вологість дорівнює {humidity}%, '
                                        f'температура становить {temperature}°C\n{size_cell}\n{consequences}\n'
                                        f'Обери покращення для свого городу.', reply_markup=kb.upgrade)

@router.callback_query(lambda c: c.data == 'Expansion')
async def Expansion(callback_query: CallbackQuery):
    await callback_query.answer()
    global humidity
    global size_cell
    global fruits
    size_cell -= 1
    if size_cell.min() == 0:
        fruits = cell_fruits * size_cell.size
        size_cell[size_cell == 0] = 10
    rand_num = random.randint(1, 40)
    if rand_num == 1 or rand_num == 2:
        app = 'Під час викопування ямок ви провалились в печеру. Ви втрачаєте один день намагаючись вибратись з неї. Ця клітинка втрачена'
        new_row = np.array([[10, 10, 'X']])
        humidity -= 10
        size_cell += 1
    elif rand_num == 3:
        app = 'Ви розумієте що на цій території пісок, а не ґрунт. Культури будуть рости довше'
        new_row = np.array([[15, 15, 15]])
    else:
        new_row = np.array([[10, 10, 10]])


    size_cell = np.vstack([size_cell, new_row])
    humidity -= 10

    await callback_query.message.edit_text(f'Твій город збільшено до \n{size_cell}\n'
                                        f'День закінчено, вологість ґрунту становить {humidity}%, '
                                        f'температура {temperature}°C, з кожної клітинки вийде {cell_fruits} плодів. Ваша кількість плодів: {fruits}', reply_markup=kb.next_day)

@router.callback_query(lambda c: c.data == 'Fertilization')
async def Fertilization(callback_query: CallbackQuery):
    global fruits
    global cell_fruits
    global humidity
    global size_cell
    size_cell -= 1
    if size_cell.min() == 0:
        fruits = cell_fruits * size_cell.size
        size_cell[size_cell == 0] = 10
    cell_fruits += 1
    cell_fruits = round(cell_fruits)
    humidity -= 10
    await callback_query.message.edit_text(f'Ти удобрив огород. Тепер з кожної клітинки вийде {cell_fruits} плодів.\n'
                                        f'День закінчено, вологість ґрунту становить {humidity}%, '
                                        f'температура {temperature}°C, ваша кількість плодів: {fruits}, розмір городу становить \n{size_cell}', reply_markup=kb.next_day)


@router.callback_query(lambda c: c.data == 'Watering')
async def Watering(callback_query: CallbackQuery):
    global fruits
    global humidity
    global size_cell
    size_cell -= 1
    if size_cell.min() == 0:
        fruits = cell_fruits * size_cell.size
        size_cell[size_cell == 0] = 10
    humidity += 30
    humidity -= 10
    await callback_query.message.edit_text(f'Ти полив город. Тепер вологість ґрунту становить {humidity}%.\n'
                                        f'День закінчено, '
                                        f'температура становить {temperature}°C, з кожної клітинки вийде {cell_fruits} плодів? розмір городу: \n{size_cell}.',
                                           reply_markup=kb.next_day)

