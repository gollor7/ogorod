import logging
import random

import math
from math import isqrt

from aiogram import Router

from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import numpy as np

from database import add_player, get_player, update_player

import plants_rpg.keybords as kb

from aiogram.enums import ParseMode

logging.basicConfig(level=logging.DEBUG)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply("Привіт, це рпг про огородника, де вам треба буде виживати як можна довше. Команда /guide щоб дізнатись правила гри,"
                        "та різні деталі, якщо граєте вперше то обов'язково до прочитання. /game щоб почати гру")

@router.message(Command('game'))
async def game_start(message: Message):
    user_id = message.from_user.id
    add_player(user_id)
    await message.reply("Ти починаєш гру з територією 3х3 клітинки, на кожній зараз росте картопля яка виросте через 10 ігрових днів.\n\n"
                        "Натискай кнопку 'Подія' щоб сталась якась подія", reply_markup=kb.event)

@router.message(Command('guide'))
async def game_start(message: Message):
    await message.reply('Гайд по грі:\n\nІгрове поле\n<blockquote expandable>На початку гри ваше ігрове поле виглядає наступним чином\n'
                        '[[10 10 10]\n[10 10 10]\n[10 10 10]]\nЦифри позначають через скільки ігрових днів виросте врожай, коли цифра стає 0, '
                        'врожай автоматично збирається та цифра знову стає 10. При деяких подіях, наприклад <b>Яма</b> цифра може стати менше 0. '
                        'Це означає що на цій клітинці яма та тут вже нічого не зможе рости.</blockquote>\n\n'
                        'Поразка\n<blockquote expandable>Ви можете програти через два фактори. Перший - <b>очки вологості</b>. Якщо у вас буде 2 очка вологості,'
                        'то на наступний день, якщо ви не виправите ситуацію ви програєте. Очки вологості набираються за умови що %вологості менший або дорівнює 0.'
                        'Очки вологості обнуляються якщо %вологості буде більший за 0 хоча б на день. '
                        'Другий фактор - <b>очки температури</b>. Поки що неактивний.</blockquote>\n\n'
                        'Початкові характеристики\n<blockquote expandable>Є два типи характеристик: Змінні та константи. Змінні: <b>Вологість</b>.'
                        'Ви починаєте гру з 45% вологості, наприкінці кожного дня вологість зменшується на 10% <spoiler>(При наявності теплиці зменшується на 5%).'
                        '</spoiler>\n<b>Температура</b>. Ви починаєте гру з температурою 19°C'
                        '', parse_mode=ParseMode.HTML)


event = {'calm weather': '🌤Спокійна, тепла погода. Температура повітря стає temp°C', 'rain': '🌧Починається дощ. Ваші рослини отримують +hum% до вологості',
         'sparrow attack': '🦤Наліт горобців. Вони їдять ваші плоди, ви втратили lost% потенційних плодів, але і 30% шкідників теж померли',
         'heat': '☀️Палюче сонце! Температура повітря стає temp°C', 'cold': '🌬Арктичні вітри! Температура повітря знижується до temp°C',
         'pit': '🕳Ви знайшли яму! Ви чітко пам\'ятаєте що раніше її тут не було. Ця клітинка втрачена',
         'cooling fertilizer': '❄️🧪На складі ви знайшли охолоджувальне добриво! Тепер ваша дія <b>Удобрення</b> Додатково зменшує температуру ґрунту на 5°C',
         'warming fertilizer': '☀️🧪На складі ви знайшли утеплювальне добриво! Тепер ваша дія <b>Удобрення</b> Додатково збільшує температуру ґрунту на 5°C',
         'moisturizing fertilizer': '💧🧪На складі ви знайшли зволожуюче добриво! Тепер ваша дія <b>Удобрення</b> Додатково збільшує вологість ґрунту на 10%',
         'dry fertilizer': '🪾🧪На складі ви знайшли сухе добриво! Тепер ваша дія <b>Удобрення</b> Додатково зменшує вологість ґрунту на 10%',
         'toxic rain': '☢️🌧Починається кислотний дощ. Ваші рослини отримують дебаф <b>Токсин</b>', 'merchant':
         '👨‍🌾Прийшов мандрівний торговець. Він пропонує різні товари, а також деталі для дивовижної технології з далеких земель - теплиці'}


max_need_humidity = 90 #%
avg_need_humidity = 45

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
    player["fertilizer_baff"] = "standart"
    player["toxic_time"] = 0
    player["a_hum"] = 0
    player['greenhouse_counter'] = 0
    player["min_need_temperature"] = 8
    player['minus_hum'] = 10
    player['goods_details'] = {
        "Тканина": "trade_greenhouse_fabric",
        "Вентиляція": "trade_greenhouse_ventilation",
        "Деревина": "trade_greenhouse_wood"
    }

    update_player(
        player["user_id"],
        humidity=player["humidity"],
        temperature=player["temperature"],
        cell_fruits=player["cell_fruits"],
        size_cell=player["size_cell"],
        fruits=player["fruits"],
        day=player["day"],
        day_humidity=player["day_humidity"],
        day_temperature=player["day_temperature"],
        fertilizer_baff=player["fertilizer_baff"],
        toxic_time=player["toxic_time"],
        a_hum=player["a_hum"],
        greenhouse_counter=player["greenhouse_counter"],
        min_need_temperature=player["min_need_temperature"],
        minus_hum=player["minus_hum"],
        goods_details=player['goods_details']
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
        day_temperature=player["day_temperature"],
        fertilizer_baff=player["fertilizer_baff"],
        toxic_time=player["toxic_time"],
        a_hum=player["a_hum"],
        greenhouse_counter=player["greenhouse_counter"],
        min_need_temperature=player["min_need_temperature"],
        minus_hum=player["minus_hum"],
        goods_details=player['goods_details']
    )

async def event_check_and_text(player, callback_query):
    consequences = ''
    text = ''
    if player["humidity"] > max_need_humidity:
        player["size_cell"] += 3
        text += '\n💧Застій води! Занадто велика вологість. Плоди ростимуть на 3 дні довше. +💀'
        player["day_humidity"] += 1
    elif player["day_humidity"] > 0 and player["humidity"] > player["a_hum"]:
        player["day_humidity"] = 0
    if player["humidity"] <= player["a_hum"]:
        text += f'\n💥Засуха! вологість ґрунту {player["a_hum"]}%. Плоди ростимуть на 2 дні довше. +💀'
        player["size_cell"] += 2
        player["day_humidity"] += 1

    elif player["day_humidity"] > 0 and player['a_hum'] < player["humidity"] < max_need_humidity:
        player["day_humidity"] = 0

    if player["temperature"] >= max_need_temperature:
        text += '\n☀️Спека! Занадто велика температура повітря. Ви втрачаєте 40% потенційних плодів. Вологість втрачається вдвічі швидше'
        player["cell_fruits"] -= player["cell_fruits"] / 100 * 40
        player["cell_fruits"] = round(player["cell_fruits"], 2)
        player["humidity"] -= player['minus_hum']
        player["day_temperature"] += 0

    elif player["day_temperature"] > 0 and player["temperature"] > 0:
        player["day_temperature"] = 0

    if player["temperature"] <= player["min_need_temperature"]:
        text += '\n❄️Заморозки! Занадто мала температура повітря. Ви втрачаєте 20% потенційних плодів'
        player["cell_fruits"] -= player["cell_fruits"] / 100 * 20
        player["cell_fruits"] = round(player["cell_fruits"], 2)
        player["day_temperature"] += 0

    elif player["day_temperature"] > 0 and player['min_need_temperature'] < player["temperature"] < player["max_need_temperature"]:
        player["day_temperature"] = 0

    if int(player['toxic_time']) > int(player['day']):
        text_toxic_time = int(player['toxic_time']) - int(player["day"])
        if text_toxic_time > 1:
            dnya_day = "дня"
        elif text_toxic_time == 1:
            dnya_day = "день"
        else:
            dnya_day = "помилка #1"
        text += f'\n☢️Ваші рослини заражені <b>Токсином</b> на {text_toxic_time} {dnya_day}. Мінімальна потрібна вологість для рослин збільшена до {player["a_hum"]}'

    if player["fertilizer_baff"] == "freeze":
        consequences += "\n❄️Добриво"
    elif player["fertilizer_baff"] == 'warm':
        consequences += "\n☀️Добриво"
    elif player['fertilizer_baff'] == 'moisturizing':
        consequences += "\n💧Добриво"
    elif player['fertilizer_baff'] == 'dry':
        consequences += '\n🪾Добриво'

    if player["day_temperature"] == 3 or player["day_humidity"] == 3:
        await callback_query.message.edit_text('Ви програли.')
        end_day = player['day']
        end_game(player)
        return "Ви", f"{end_day}"

    save_player(player)
    return text, consequences


@router.callback_query(lambda c: c.data == 'pick_event' or c.data == "next_day")
async def start_event(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    player = get_player(user_id)

    if not player:
        add_player(user_id)
        player = get_player(user_id)

    random_event = random.choice(list(event.keys()))
    #random_event = "merchant"

    text = ''

    if int(player["toxic_time"]) > int(player['day']):
        player["a_hum"] -= 10
    else:
        player['a_hum'] = 0

    if random_event == "calm weather":
        a = 14 + isqrt(player["day"])
        b = 24 + isqrt(player["day"])
        temp = random.randint(round(a, 0), round(b, 0))
        text = event[random_event].replace("temp", str(temp))
        player["temperature"] = temp

    elif random_event == 'rain':
        b = 30 + isqrt(player["day"])
        hum = random.randint(10, round(b, 0))
        text = event[random_event].replace("hum", str(hum))
        player["humidity"] += hum

    elif random_event == 'sparrow attack':
        a = 10 + isqrt(player["day"])
        b = 30 + isqrt(player["day"])
        lost = random.randint(round(a, 0), round(b, 0))
        text = event[random_event].replace("lost", str(lost))
        if player["temperature"] < avg_need_temperature:
            player["temperature"] += 1
        elif player["temperature"] > avg_need_temperature:
            player["temperature"] -= 1
        player["cell_fruits"] -= player["cell_fruits"] / 100 * lost
        player["cell_fruits"] = round(player["cell_fruits"], 2)

    elif random_event == 'heat':
        a = 30 + isqrt(player["day"])
        b = 40 + isqrt(player["day"])
        temp = random.randint(round(a, 0), round(b, 0))
        text = event[random_event].replace("temp", str(temp))
        player["temperature"] = temp

    elif random_event == "cold":
        a = 0 - isqrt(player["day"])
        b = 8 - isqrt(player["day"])
        temp = random.randint(round(a, 0), round(b, 0))
        text = event[random_event].replace("temp", str(temp))
        player["temperature"] = temp

    elif random_event == 'pit':
        text = event[random_event]
        rows, cols = player["size_cell"].shape
        rand_row = random.randint(0, rows - 1)
        rand_col = random.randint(0, cols - 1)
        player["size_cell"][rand_row, rand_col] = -10

    elif random_event == 'cooling fertilizer':
        text = event[random_event]
        player["fertilizer_baff"] = "freeze"
        if player["temperature"] < avg_need_temperature:
            player["temperature"] += 1
        elif player["temperature"] > avg_need_temperature:
            player["temperature"] -= 1

    elif random_event == 'warming fertilizer':
        text = event[random_event]
        player["fertilizer_baff"] = "warm"
        if player["temperature"] < avg_need_temperature:
            player["temperature"] += 1
        elif player["temperature"] > avg_need_temperature:
            player["temperature"] -= 1

    elif random_event == 'moisturizing fertilizer':
        text = event[random_event]
        player['fertilizer_baff'] = 'moisturizing'
        if player["temperature"] < avg_need_temperature:
            player["temperature"] += 1
        elif player["temperature"] > avg_need_temperature:
            player["temperature"] -= 1

    elif random_event == 'dry fertilizer':
        text = event[random_event]
        player['fertilizer_baff'] = 'dry'
        if player["temperature"] < avg_need_temperature:
            player["temperature"] += 1
        elif player["temperature"] > avg_need_temperature:
            player["temperature"] -= 1

    elif random_event == 'toxic rain':
        text = event[random_event]
        player['toxic_time'] = player['day'] + 4
        player["a_hum"] = 40 + 4 * isqrt(player['day'])

    elif random_event == 'merchant':
        goods_fertilizer = {'❄️🧪Охолоджувальне добриво: 50': 'trade_cooling fertilizer', '☀️🧪Утеплювальне добриво: 50': 'trade_warming fertilizer',
                            '💧🧪Зволожуюче добриво: 50': 'trade_moisturizing fertilizer', '🪾🧪Сухе добриво: 50': 'trade_dry fertilizer'}
        goods_details = player['goods_details']
        print(goods_details)
        print(player['goods_details'])

        fertilizer_sale = random.sample(list(goods_fertilizer.items()), 2)
        if not goods_details:
            details_sale = ['Деталі закінчились', 'no_details']
        else:
            details_sale = random.choice(list(player['goods_details'].items()))
            print(player['goods_details'])

        sales = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=fertilizer_sale[0][0], callback_data=fertilizer_sale[0][1]),
             InlineKeyboardButton(text=fertilizer_sale[1][0], callback_data=fertilizer_sale[1][1])],
            [InlineKeyboardButton(text=details_sale[0], callback_data=details_sale[1])],
            [InlineKeyboardButton(text='Нічого не купувати', callback_data='trade_nothing')]
             ])

        await callback_query.message.edit_text(f'{event[random_event]}', reply_markup = sales)


        if player["temperature"] < avg_need_temperature:
            player["temperature"] += 1
        elif player["temperature"] > avg_need_temperature:
            player["temperature"] -= 1

        return



    else:
        text = 'Помилка: Жодної події не знайдено'



    save_player(player)

    add_text, consequences = await event_check_and_text(player, callback_query)
    if add_text == "Ви":
        await callback_query.message.edit_text(f'Ви програли. День: {consequences}')
        return
    full_text = f'{text}\n{add_text}'

    await callback_query.message.edit_text(
        f'{full_text}\nПотенційна кількість плодів з клітинки: {player["cell_fruits"]}.\n'
        f'Вологість дорівнює {player["humidity"]}%.\n'
        f'Температура становить {player["temperature"]}°C\n{player["size_cell"]}\n{consequences}\n'
        f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
        f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>.\n'
        f'Обери покращення для свого городу:', parse_mode=ParseMode.HTML, reply_markup=kb.upgrade)

@router.callback_query(lambda c: c.data.startswith("trade"))
async def trader_callback(callback_query: CallbackQuery):

    user_id = callback_query.from_user.id
    player = get_player(user_id)
    text = ''

    if callback_query.data == 'trade_cooling fertilizer':
        if player['fruits'] >= 50:
            player['fruits'] -= 50
            player["fertilizer_baff"] = "freeze"
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_warming fertilizer':
        if player['fruits'] >= 50:
            player['fruits'] -= 50
            player["fertilizer_baff"] = "warm"
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_moisturizing fertilizer':
        if player['fruits'] >= 50:
            player['fruits'] -= 50
            player['fertilizer_baff'] = 'moisturizing'
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_dry fertilizer':
        if player['fruits'] >= 50:
            player['fruits'] -= 50
            player['fertilizer_baff'] = 'dry'
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_greenhouse_fabric':
        if player['fruits'] >= 80:
            player['fruits'] -= 80
            player["greenhouse_counter"] += 1
            del player['goods_details']["Тканина: 80"]
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_greenhouse_ventilation':
        if player['fruits'] >= 100:
            player['fruits'] -= 100
            player["greenhouse_counter"] += 1
            del player['goods_details']["Вентиляція: 100"]
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_greenhouse_wood':
        if player['fruits'] >= 90:
            player['fruits'] -= 90
            player["greenhouse_counter"] += 1
            del player['goods_details']["Деревина: 90"]
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_nothing':
        pass
    elif callback_query.data == 'no_details':
        await callback_query.answer(text='Деталей вже не залишилось', show_alert=True)
        return

    if player["greenhouse_counter"] == 3:
        text = ('Ви закінчили побудову теплиці. Тепер культури будуть менше мерзнути, та вода буде повільніше випаровуватись. '
                '+15 до мінімальної допустимої температури, +5% до вологості кожен день\n')
        player['min_need_temperature'] = -7
        player['minus_hum'] -= 5
        player['greenhouse_counter'] = 0

    print(f'{player['greenhouse_counter']}')

    add_text, consequences = await event_check_and_text(player, callback_query)
    if add_text == "Ви":
        await callback_query.message.edit_text(f'Ви програли. День: {consequences}')
        return
    full_text = f'{text}\n{add_text}'

    await callback_query.message.edit_text(
        f'{full_text}\nПотенційна кількість плодів з клітинки: {player["cell_fruits"]}.\n'
        f'Вологість дорівнює {player["humidity"]}%.\n'
        f'Температура становить {player["temperature"]}°C\n{player["size_cell"]}\n{consequences}\n'
        f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
        f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>.\n'
        f'Обери покращення для свого городу:', parse_mode=ParseMode.HTML, reply_markup=kb.upgrade)









@router.callback_query(lambda c: c.data == 'Expansion')
async def Expansion(callback_query: CallbackQuery):
    await callback_query.answer()

    user_id = callback_query.from_user.id
    player = get_player(user_id)

    if not player:
        add_player(user_id)
        player = get_player(user_id)

    if player["size_cell"].shape[0] == 10:
        await callback_query.message.edit_text('Ваша територія закінчилась, більше розширятись не вийде. Оберіть інше покращення', reply_markup=kb.upgrade)
        return

    player["size_cell"] -= 1

    if np.any(player["size_cell"] == 0):
        player["fruits"] += np.count_nonzero(player['size_cell'] == 0) * player['cell_fruits']
        player['fruits'] = round(player["fruits"], 0)
        print(player['fruits'])
        player["size_cell"][player["size_cell"] == 0] = 10
    rand_num = random.randint(1, 40)
    if rand_num == 1 or rand_num == 2:
        app = '🕳Під час викопування ямок ви провалились в печеру. Ви втрачаєте один день намагаючись вибратись з неї. Ця клітинка втрачена'
        new_row = np.array([[10, 10, -10]])
        player["humidity"] -= player['minus_hum']
        player["size_cell"] += 1
    elif rand_num == 3:
        app = '🪨Ви розумієте що на цій території багато каміння. Культури будуть рости довше'
        new_row = np.array([[15, 15, 15]])
    else:
        new_row = np.array([[10, 10, 10]])
        app = ''


    player["size_cell"] = np.vstack([player["size_cell"], new_row])
    player["humidity"] -= player['minus_hum']

    player["day"] += 1

    save_player(player)

    await callback_query.message.edit_text(f'{app}\n'
                                           f'Твій город збільшено до \n{player["size_cell"]}\n\n'
                                        f'📆День {player["day"]} закінчено.\n'
                                           f'Вологість ґрунту становить {player["humidity"]}%.\n'
                                        f'Температура {player["temperature"]}°C.\n'
                                           f'З кожної клітинки вийде {player["cell_fruits"]} плодів.\n'
                                           f'Ваша кількість плодів: {player["fruits"]}.\n'
                                           f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
                                           f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>', reply_markup=kb.next_day, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data == 'Fertilization')
async def Fertilization(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    player = get_player(user_id)

    if not player:
        add_player(user_id)
        player = get_player(user_id)

    fert_text = ""

    match player["fertilizer_baff"]:
        case "standart":
            player["cell_fruits"] += 1
            fert_text = 'Ти удобрив огород'
        case "freeze":
            player["cell_fruits"] += 1
            player["temperature"] -= 5
            fert_text = 'Ти удобрив огород та зменшив температуру ґрунту на 5°C'
        case "warm":
            player["cell_fruits"] += 1
            player["temperature"] += 5
            fert_text = 'Ти удобрив огород та зменшив температуру ґрунту на 5°C'
        case 'moisturizing':
            player["cell_fruits"] += 1
            player["humidity"] += 10
            fert_text = 'Ти удобрив огород та збільшив вологість ґрунту на 10%'
        case 'dry':
            player['cell_fruits'] += 1
            player['humidity'] -= 10
            fert_text = 'Ти удобрив огород та зменшив вологість ґрунту на 10%'

    player["size_cell"] -= 1
    if np.any(player["size_cell"] == 0):
        player["fruits"] += np.count_nonzero(player['size_cell'] == 0) * player['cell_fruits']
        player['fruits'] = round(player["fruits"], 0)
        print(player['fruits'])
        player["size_cell"][player["size_cell"] == 0] = 10
    player["cell_fruits"] += 1
    player["cell_fruits"] = round(player["cell_fruits"])
    player["humidity"] -= player['minus_hum']

    player["day"] += 1

    save_player(player)

    await callback_query.message.edit_text(f'{fert_text}. Тепер з кожної клітинки вийде {player["cell_fruits"]} плодів.\n'
                                        f'📆День {player["day"]} закінчено.\n'
                                           f'Вологість ґрунту становить {player["humidity"]}%.\n'
                                        f'Температура {player["temperature"]}°C.\n'
                                           f'Ваша кількість плодів: {player["fruits"]}.\n'
                                           f'Розмір городу становить \n{player["size_cell"]}.\n\n'
                                           f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
                                           f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>', reply_markup=kb.next_day, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data == 'Watering')
async def Watering(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    player = get_player(user_id)

    if not player:
        add_player(user_id)
        player = get_player(user_id)

    player["size_cell"] -= 1
    if np.any(player["size_cell"] == 0):
        player["fruits"] += np.count_nonzero(player['size_cell'] == 0) * player['cell_fruits']
        player['fruits'] = round(player["fruits"], 0)
        print(player['fruits'])
        player["size_cell"][player["size_cell"] == 0] = 10
    player["humidity"] += 30
    player["humidity"] -= player['minus_hum']
    player["temperature"] -= 3

    player["day"] += 1

    save_player(player)

    await callback_query.message.edit_text(f'Ти полив огород. Тепер вологість ґрунту становить {player["humidity"]}%. Температура зменшена на 3°C.\n'
                                           f'📆День {player["day"]} закінчено.\n'
                                        f'Температура {player["temperature"]}°C.\n'
                                           f'З кожної клітинки вийде {player["cell_fruits"]} плодів.\n'
                                           f'Ваша кількість плодів: {player["fruits"]}.\n'
                                           f'Розмір городу: \n{player["size_cell"]}.\n\n'
                                           f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
                                           f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>', reply_markup=kb.next_day, parse_mode=ParseMode.HTML)

