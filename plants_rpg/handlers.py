import logging
import random
import asyncio

from math import isqrt

from aiogram import Router

from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import numpy as np

from database import add_player, get_player, update_player

import plants_rpg.keybords as kb

from aiogram.enums import ParseMode

logging.basicConfig(level=logging.DEBUG)
router = Router()

edit_lock = asyncio.Lock()

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
                        'Поразка\n<blockquote expandable>Ви можете програти через два фактори. Перший - <b>очки вологості</b>. Якщо у вас буде 3 очка вологості, '
                        'то на наступний день, якщо ви не виправите ситуацію ви програєте. Очки вологості набираються за умови що % вологості менший або дорівнює 0, або '
                        'якщо % вологості більший за 100%. Очки вологості обнуляються якщо % вологості буде більший за 0% та менший за 100% хоча б на день. '
                        'Другий фактор - <b>Очки температури</b>. Якщо у вас буде 3 очка температури, то на наступний день, якщо ви не виправите ситуацію ви програєте. '
                        'Очки температури набираються за умови що температура буде більшою за 30°C, або меншою за 0°C <span class="tg-spoiler">'
                        '(З теплицею мінімальна температура зменшується до -7°C).</span></blockquote>\n\n'
                        'Початкові характеристики\n<blockquote expandable>Є два типи характеристик: Змінні та константи. Змінні: <b>Вологість</b>\n'
                        'Ви починаєте гру з 45% вологості, наприкінці кожного дня вологість зменшується на 10% <span class="tg-spoiler">'
                        '(При наявності теплиці зменшується на 5%).</span> На вологість впливають деякі <b>Події</b>, такі як <b>Дощ</b>, <b>Кислотний дощ</b>, '
                        '<b>Спека</b>, і т.д. А також дія <b>Поливання</b> додає до вологості 30%, а <b>Підгортання</b> навпаки зменшує на 10%. '
                        '\n<b>Температура</b>\nВи починаєте гру з температурою 19°C. На температуру впливають події погоди, також подія <b>Пожежа</b> накладає стан '
                        '<b>Горіння</b> який кожен хід збільшує температуру в залежності від вашого дня. Також <b>Поливання</b> зменшує температуру на 5°C, '
                        'а <b>Підгортання</b> навпаки збільшує на 7°C. Також іноді температура сама по собі зменшується або збільшується до 19°C.</blockquote>\n\n'
                        'Події\n<blockquote expandable>'
                        , parse_mode=ParseMode.HTML)


event = {'calm weather': '🌤Спокійна, тепла погода. Температура повітря стає temp°C.', 'rain': '🌦Починається дощ. Ваші рослини отримують +hum% до вологості.',
         'sparrow attack': '🦤Наліт горобців. Вони їдять ваші плоди, ви втратили lost% потенційних плодів, але і 30% шкідників теж померли.',
         'heat': '☀️Палюче сонце! Температура повітря стає temp°C.', 'cold': '🌬Арктичні вітри! Температура повітря знижується до temp°C.',
         'pit': '🕳Ви знайшли яму! Ви чітко пам\'ятаєте що раніше її тут не було. Ця клітинка втрачена.',
         'cooling fertilizer': '❄️🧪На складі ви знайшли охолоджувальне добриво! Тепер ваша дія <b>Удобрення</b> Додатково зменшує температуру ґрунту на 10°C.',
         'warming fertilizer': '☀️🧪На складі ви знайшли утеплювальне добриво! Тепер ваша дія <b>Удобрення</b> Додатково збільшує температуру ґрунту на 10°C.',
         'moisturizing fertilizer': '💧🧪На складі ви знайшли зволожуюче добриво! Тепер ваша дія <b>Удобрення</b> Додатково збільшує вологість ґрунту на 15%.',
         'dry fertilizer': '🌾🧪На складі ви знайшли сухе добриво! Тепер ваша дія <b>Удобрення</b> Додатково зменшує вологість ґрунту на 15%.',
         'toxic rain': '☢️🌧Починається кислотний дощ. Ваші рослини отримують дебаф <b>Токсин</b>.', 'merchant':
         '👨‍🌾Прийшов мандрівний торговець. Він пропонує різні товари, а також деталі для дивовижної технології з далеких земель - теплиці.',
         'rainstorm': '🌧Ви бачите як над вами згущаються хмари... Починається злива. Ваші рослини отримують +hum% до вологості та -temp°C до температури.', 'earthquake':
         '🌋Ви відчуваєте як земля під вами починає трястись, навряд чи це піде на користь рослинами.',
         'fire': '🔥Ви бачите як з городу йде дим, починається пожежа. Ваші рослини отримують дебаф <b>Горіння</b>.',
         'rainbow': '🌈Прекрасна погода! Рослини отримують ефект <b>Плодючість</b> на 3 дні. '
                    'Потенційна кількість плодів з клітинки збільшується на 2 кожен день. Температура стає 19 градусів, вологість 50%',
         'Late blight':
             '🦠⚫️Заглядаючи під листя однієї з рослин ви помічаєте темні плями на листі. Ваша картопля заражена <b>Темною пліснявою</b> на Х днів. Ріст рослин зупинено',
         'Silver scab':'🦠🪙Ви помічаєте що ваші рослини втрачають вологу швидше, ніж зазвичай. Оглядаючи стебла, ви розумієте що весь город заражений <b>Срібною паршою</b>',
         'Pandora\'s box': '📦В одному з мішків ви знаходите дивну коробочку. Ви відкриваєте її, та розумієте що це <b>Скринька пандори</b>! Температура різко змінюється до '
                           'temp°C, вологість стає hum%, та ви отримуєте статус status! На day dnya.'}

status_effect = ['toxic_time', 'fire_time', 'fertility_time', 'late_blight_time', 'silver_scab_time']


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
    player["fire_time"] = 0
    player["fertility_time"] = 0
    player['god_blessing_time'] = 0
    player['late_blight_time'] = 0
    player['silver_scab_time'] = 0

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
        goods_details=player['goods_details'],
        fire_time=player['fire_time'],
        fertility_time=player['fertility_time'],
        god_blessing_time=player['god_blessing_time'],
        late_blight_time=player['late_blight_time'],
        silver_scab_time=player['silver_scab_time']
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
        goods_details=player['goods_details'],
        fire_time=player['fire_time'],
        fertility_time=player['fertility_time'],
        god_blessing_time=player['god_blessing_time'],
        late_blight_time=player['late_blight_time'],
        silver_scab_time=player['silver_scab_time']
    )

def check_fertilizer(player):
    consequences = ''
    if player["fertilizer_baff"] == "freeze":
        consequences += "\n❄️Добриво"
    elif player["fertilizer_baff"] == 'warm':
        consequences += "\n☀️Добриво"
    elif player['fertilizer_baff'] == 'moisturizing':
        consequences += "\n💧Добриво"
    elif player['fertilizer_baff'] == 'dry':
        consequences += '\n🌾Добриво'
    return consequences

async def event_check_and_text(player):
    text = ''

    if player['god_blessing_time'] > player['day']:
        text_god_blessing_time = player['god_blessing_time'] - player['day']

        player['temperature'] = 19

        if player['a_hum'] > 50:
            player['humidity'] = player['a_hum']
        else:
            player['humidity'] = 50

        if text_god_blessing_time > 1:
            dnya_day = "дні"
        elif text_god_blessing_time == 1:
            dnya_day = "день"
        else:
            dnya_day = "помилка #1"

        text += f'\n✨Ви маєте <b>Божественне благословіння</b> на ще {text_god_blessing_time} {dnya_day}. Температура стає 19°C, Вологість - {player['humidity']}%\n'


    if player["fire_time"] > player["day"]:
        text_fire_time = player["fire_time"] - player["day"]

        plus_temp = round((3 + isqrt(player["day"])), 0)
        player["temperature"] += plus_temp

        minus_hum = round((5 + 2 * isqrt(player["day"])), 0)
        player['humidity'] -= minus_hum

        rows, cols = player["size_cell"].shape
        rand_row = random.randint(0, rows - 1)
        rand_col = random.randint(0, cols - 1)
        plus_cell = round((2 + isqrt(player["day"])), 0)
        if player["size_cell"][rand_row, rand_col] > 0:
            player["size_cell"][rand_row, rand_col] += plus_cell

        if text_fire_time > 1:
            dnya_day = "дні"
        elif text_fire_time == 1:
            dnya_day = "день"
        else:
            dnya_day = "помилка #1"

        text += (f'\n🔥Ваші рослини <b>Горять</b> ще {text_fire_time} {dnya_day}. Температура збільшена на {plus_temp}°C, вологість зменшена на {minus_hum},'
                 f' Деякі рослини ростимуть на {plus_cell} довше\n')


    if int(player['toxic_time']) > int(player['day']):
        text_toxic_time = int(player['toxic_time']) - int(player["day"])
        if text_toxic_time > 1:
            dnya_day = "дні"
        elif text_toxic_time == 1:
            dnya_day = "день"
        else:
            dnya_day = "помилка #1"
        text += f'\n☢️Ваші рослини заражені <b>Токсином</b> на {text_toxic_time} {dnya_day}. Мінімальна потрібна вологість для рослин збільшена до {player["a_hum"]}.\n'


    if player['fertility_time'] > player['day']:
        text_fertility_time  = player['fertility_time'] - player['day']

        player['cell_fruits'] += 2

        if text_fertility_time > 1:
            dnya_day = "дні"
        elif text_fertility_time == 1:
            dnya_day = "день"
        else:
            dnya_day = "помилка #1"

        text += f'\n🌈Ваші рослини маю баф <b>Плодючість</b> на {text_fertility_time} {dnya_day}. Потенційна кількість плодів збільшена до {player['cell_fruits']}.\n'


    if player['late_blight_time'] > player['day']:
        text_late_blight_time = player['late_blight_time'] - player['day']

        if 5 > text_late_blight_time > 1:
            dnya_day = "дні"
        elif text_late_blight_time == 1:
            dnya_day = "день"
        elif text_late_blight_time > 5:
            dnya_day = 'днів'
        else:
            dnya_day = "помилка #1"

        text += f'\n🦠⚫Ваші рослини заражені <b>Чорною пліснявою</b> ще на {text_late_blight_time} {dnya_day}! Ріст рослин зупинено.\n'


    if player['silver_scab_time'] > player['day']:
        text_silver_scab_time = player['silver_scab_time'] - player['day']

        player['humidity'] -= 10

        if 5 > text_silver_scab_time > 1:
            dnya_day = "дні"
        elif text_silver_scab_time == 1:
            dnya_day = "день"
        elif text_silver_scab_time >= 5:
            dnya_day = 'днів'
        else:
            dnya_day = "помилка #1"

        text += f'\n🦠🪙Ваші рослини заражені <b>Срібною паршою</b> на {text_silver_scab_time} {dnya_day}! Вологість втрачається швидше на 10% кожен день.\n'


    if player["humidity"] > max_need_humidity:
        player["size_cell"] += 3
        text += '\n💧Застій води! Занадто велика вологість. Плоди ростимуть на 3 дні довше. +💀'
        player["day_humidity"] += 1
    elif player["day_humidity"] > 0 and player["humidity"] > player["a_hum"]:
        player["day_humidity"] = 0
    if player["humidity"] <= player["a_hum"]:
        text += f'\n💥Засуха! вологість ґрунту {player["humidity"]}%. Плоди ростимуть на 2 дні довше. +💀'
        player["size_cell"] += 2
        player["day_humidity"] += 1

    elif player["day_humidity"] > 0 and player['a_hum'] < player["humidity"] < max_need_humidity:
        player["day_humidity"] = 0

    if player["temperature"] >= max_need_temperature:
        text += '\n☀️Спека! Занадто велика температура повітря. Ви втрачаєте 40% потенційних плодів. Вологість втрачається вдвічі швидше. +💀'
        player["cell_fruits"] -= player["cell_fruits"] / 100 * 40
        player["cell_fruits"] = round(player["cell_fruits"], 2)
        player["humidity"] -= player['minus_hum']
        player["day_temperature"] += 1

    elif player["day_temperature"] > 0 and player["temperature"] > 0:
        player["day_temperature"] = 0

    if player["temperature"] <= player["min_need_temperature"]:
        text += '\n❄️Заморозки! Занадто мала температура повітря. Ви втрачаєте 20% потенційних плодів. +💀'
        player["cell_fruits"] -= player["cell_fruits"] / 100 * 20
        player["cell_fruits"] = round(player["cell_fruits"], 2)
        player["day_temperature"] += 1

    elif player["day_temperature"] > 0 and player['min_need_temperature'] < player["temperature"] < max_need_temperature:
        player["day_temperature"] = 0

    save_player(player)
    return text

@router.callback_query(lambda c: c.data == 'pick_event' or c.data == "next_day")
async def start_event(callback_query: CallbackQuery):
    if edit_lock.locked():
        await callback_query.answer("⏳ Зачекай, дію вже виконуємо...", show_alert=False)
        return
    async with edit_lock:
        await callback_query.answer()
        user_id = callback_query.from_user.id
        player = get_player(user_id)

        if not player:
            add_player(user_id)
            player = get_player(user_id)
        probabilities = [20, 20, 20, 20, 20, 20, 14, 14, 14, 12, 12, 28, 8, 6, 4, 5, 5, 6, 6]
        random_event = random.choices(list(event.keys()), probabilities)[0]
        if player['min_need_temperature'] < player['temperature'] < max_need_temperature and player['day_temperature'] < 1:
            pass
        else:
            while random_event in ['cold', 'heat']:
                random_event = random.choices(list(event.keys()), probabilities)[0]

        #random_event = "merchant"

        consequences = check_fertilizer(player)

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
            if player["fire_time"] > player["day"]:
                player["fire_time"] -= 1
                text += ' Дощ затушив деякі осередки вогню'

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
            if player["temperature"] < -4 and player["fire_time"] > player["day"]:
                player['fire_time'] = 0
                text += ' Через сильні морози вогонь затух сам по собі'

        elif random_event == 'pit':
            text = event[random_event]
            rows, cols = player["size_cell"].shape
            rand_row = random.randint(0, rows - 1)
            rand_col = random.randint(0, cols - 1)
            player["size_cell"][rand_row, rand_col] = -10

        elif random_event == 'cooling fertilizer':
            if player["temperature"] < avg_need_temperature:
                player["temperature"] += 1
            elif player["temperature"] > avg_need_temperature:
                player["temperature"] -= 1

            text = event[random_event]

            fertilizer_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Взяти', callback_data='pick_cooling'),
                 InlineKeyboardButton(text='Залишити', callback_data='pick_leave')]
            ])

            await callback_query.message.edit_text(f'{text}\nВологість: {player['humidity']}%.\n'
                                                   f'Температура: {player["temperature"]}.\n'
                                                   f'{consequences}',
                                                   reply_markup=fertilizer_kb, parse_mode=ParseMode.HTML)
            return

        elif random_event == 'warming fertilizer':
            if player["temperature"] < avg_need_temperature:
                player["temperature"] += 1
            elif player["temperature"] > avg_need_temperature:
                player["temperature"] -= 1

            text = event[random_event]

            fertilizer_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Взяти', callback_data='pick_warm'),
                 InlineKeyboardButton(text='Залишити', callback_data='pick_leave')]
            ])

            await callback_query.message.edit_text(f'{text}\nВологість: {player['humidity']}.\n'
                                                   f'Температура: {player["temperature"]}.\n'
                                                   f'{consequences}',
                                                   reply_markup=fertilizer_kb, parse_mode=ParseMode.HTML)
            return

        elif random_event == 'moisturizing fertilizer':
            if player["temperature"] < avg_need_temperature:
                player["temperature"] += 1
            elif player["temperature"] > avg_need_temperature:
                player["temperature"] -= 1

            text = event[random_event]

            fertilizer_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Взяти', callback_data='pick_moisturizing'),
                 InlineKeyboardButton(text='Залишити', callback_data='pick_leave')]
            ])

            await callback_query.message.edit_text(f'{text}\nВологість: {player['humidity']}.\n'
                                                   f'Температура: {player["temperature"]}.\n'
                                                   f'{consequences}',
                                                   reply_markup=fertilizer_kb, parse_mode=ParseMode.HTML)
            return

        elif random_event == 'dry fertilizer':
            if player["temperature"] < avg_need_temperature:
                player["temperature"] += 1
            elif player["temperature"] > avg_need_temperature:
                player["temperature"] -= 1

            text = event[random_event]

            fertilizer_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Взяти', callback_data='pick_dry'),
                 InlineKeyboardButton(text='Залишити', callback_data='pick_leave')]
            ])

            await callback_query.message.edit_text(f'{text}\nВологість: {player['humidity']}.\n'
                                                   f'Температура: {player["temperature"]}.\n'
                                                   f'{consequences}',
                                                   reply_markup=fertilizer_kb, parse_mode=ParseMode.HTML)
            return

        elif random_event == 'toxic rain':
            text = event[random_event]
            player['toxic_time'] = player['day'] + 4
            player["a_hum"] = 40 + 4 * isqrt(player['day'])

        elif random_event == 'rainstorm':
            b_hum = 50 + isqrt(player["day"])
            b_temp = 10 + isqrt(player["day"])
            hum = random.randint(30, round(b_hum, 0))
            temp = random.randint(5, round(b_temp, 0))
            text = event[random_event].replace("hum", str(hum))
            text = text.replace("temp", str(temp))
            player["humidity"] += hum
            if player["fire_time"] > player["day"]:
                player["fire_time"] = 0
                text += ' Злива потушила вогонь'

        elif random_event == 'earthquake':
            text = event[random_event]
            rows, cols = player["size_cell"].shape
            pit_count = random.randint(2, 5)
            for _ in range(pit_count):
                rand_row = random.randint(0, rows - 1)
                rand_col = random.randint(0, cols - 1)
                player["size_cell"][rand_row, rand_col] = -10
        elif random_event == 'merchant':
            goods_fertilizer = {'❄️🧪Охолоджувальне добриво: 40': 'trade_cooling fertilizer', '☀️🧪Утеплювальне добриво: 40': 'trade_warming fertilizer',
                                '💧🧪Зволожуюче добриво: 40': 'trade_moisturizing fertilizer', '🪾🧪Сухе добриво: 40': 'trade_dry fertilizer'}
            goods_details = player['goods_details']

            fertilizer_sale = random.sample(list(goods_fertilizer.items()), 2)
            if not goods_details:
                details_sale = ['Деталі закінчились', 'no_details']
            else:
                details_sale = random.choice(list(player['goods_details'].items()))

            sales = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=fertilizer_sale[0][0], callback_data=fertilizer_sale[0][1]),
                 InlineKeyboardButton(text=fertilizer_sale[1][0], callback_data=fertilizer_sale[1][1])],
                [InlineKeyboardButton(text=details_sale[0], callback_data=details_sale[1])],
                [InlineKeyboardButton(text='Нічого не купувати', callback_data='trade_nothing')]
                 ])

            await callback_query.message.edit_text(f'{event[random_event]}\nВаша кількість плодів: {player['fruits']}', reply_markup = sales)


            if player["temperature"] < avg_need_temperature:
                player["temperature"] += 1
            elif player["temperature"] > avg_need_temperature:
                player["temperature"] -= 1

            return

        elif random_event == 'fire':
            text = event[random_event]
            player["fire_time"] = player["day"] + 3

        elif random_event == 'rainbow':
            text = event[random_event]
            player['fertility_time'] = player['day'] + 3
            player['temperature'], player['humidity'] = 19, 50

        elif random_event == 'Late blight':
            player['late_blight_time'] = player['day'] + isqrt(player['day']) / 1.5
            player['late_blight_time'] = round(player['late_blight_time'])
            text_late_blight_time = player['late_blight_time'] - player['day']
            text = event[random_event].replace('Х', str(text_late_blight_time))

        elif random_event == 'Silver scab':
            text = event[random_event]
            player['silver_scab_time'] = player['day'] + isqrt(player['day']) / 1.5
            player['silver_scab_time'] = round(player['silver_scab_time'])

        elif random_event == 'Pandora\'s box':
            status = ''

            a_temp = 10 - round(1.5 * isqrt(player['day']))
            b_temp = 30 + round(1.5 * isqrt(player['day']))
            player['temperature'] = random.randint(a_temp, b_temp)

            a_hum = 0 - round(2 * isqrt(player['day']))
            b_hum = 80 + round(2 * isqrt(player['day']))
            player['humidity'] = random.randint(a_hum, b_hum)

            random_status = random.choice(status_effect)

            day = round(isqrt(player['day']) / 2)

            player[random_status] = player['day'] + day

            if 5 > day > 1:
                dnya = "дні"
            elif day == 1:
                dnya = "день"
            elif day >= 5:
                dnya = 'днів'
            else:
                dnya = "помилка #1"

            match random_status:
                case 'toxic_time':
                    status = 'Токсин'
                    player["a_hum"] = 40 + 4 * isqrt(player['day'])
                case 'fire_time':
                    status = 'Вогонь'
                case 'fertility_time':
                    status = 'Плодючість'
                    player['temperature'], player['humidity'] = 19, 50
                case 'late_blight_time':
                    status = 'Чорна пліснява'
                case 'silver_scab_time':
                    status = 'Срібна парша'

            text = event[random_event].replace('temp', str(player['temperature']))
            text = text.replace('hum', str(player['humidity']))
            text = text.replace('status', status)
            text = text.replace('day', str(day))
            text = text.replace('dnya', str(dnya))

        else:
            text = 'Помилка: Жодної події не знайдено'

        save_player(player)

        add_text = await event_check_and_text(player)
        if add_text == "Ви":
            await callback_query.message.edit_text(f'Ви програли. День: {player["day"]}')
            return
        full_text = f'{text}\n{add_text}'

        await asyncio.sleep(0.7)

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

    consequences = check_fertilizer(player)

    if callback_query.data == 'trade_cooling fertilizer':
        if player['fruits'] >= 40:
            player['fruits'] -= 40
            player["fertilizer_baff"] = "freeze"
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_warming fertilizer':
        if player['fruits'] >= 40:
            player['fruits'] -= 40
            player["fertilizer_baff"] = "warm"
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_moisturizing fertilizer':
        if player['fruits'] >= 40:
            player['fruits'] -= 40
            player['fertilizer_baff'] = 'moisturizing'
        else:
            await callback_query.answer(text='У вас недостатньо плодів для купівлі', show_alert=True)
            return
    elif callback_query.data == 'trade_dry fertilizer':
        if player['fruits'] >= 40:
            player['fruits'] -= 40
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
        text = ('Ви закінчили побудову 🏠<b>теплиці</b>. Тепер культури будуть менше мерзнути, та вода буде повільніше випаровуватись. '
                '+15 до мінімальної допустимої температури, +5% до вологості кожен день\n')
        player['min_need_temperature'] = -7
        player['minus_hum'] -= 5
        player['greenhouse_counter'] = 0

    add_text = await event_check_and_text(player)
    if add_text == "Ви":
        await callback_query.message.edit_text(f'Ви програли. День: {player['day']}')
        return
    full_text = f'{text}\n{add_text}'

    await callback_query.message.edit_text(
        f'{full_text}\nПотенційна кількість плодів з клітинки: {player["cell_fruits"]}.\n'
        f'Вологість дорівнює {player["humidity"]}%.\n'
        f'Температура становить {player["temperature"]}°C\n{player["size_cell"]}\n{consequences}\n'
        f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
        f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>.\n'
        f'Обери покращення для свого городу:', parse_mode=ParseMode.HTML, reply_markup=kb.upgrade)


@router.callback_query(lambda c: c.data.startswith("pick"))
async def fertilizer_choose(callback_query: CallbackQuery):
    if edit_lock.locked():
        await callback_query.answer("⏳ Зачекай, дію вже виконуємо...", show_alert=False)
        return
    async with edit_lock:
        user_id = callback_query.from_user.id
        player = get_player(user_id)

        app = ''

        if callback_query.data == 'pick_leave':
            text = 'Ви вирішили залишитись при своєму'
        elif callback_query.data == 'pick_cooling':
            player['fertilizer_baff'] = 'freeze'
            text = 'Ви вирішили взяти ❄️Добриво'
        elif callback_query.data == 'pick_warm':
            player['fertilizer_baff'] = 'warm'
            text = 'Ви вирішили взяти ☀️Добриво'
        elif callback_query.data == 'pick_moisturizing':
            player['fertilizer_baff'] = 'moisturizing'
            text = 'Ви вирішили взяти 💧Добриво'
        elif callback_query.data == 'pick_dry':
            player['fertilizer_baff'] = 'dry'
            text = 'Ви вирішили взяти 🌾Добриво'
        else:
            text = 'Невідомий колбек'

        consequences = check_fertilizer(player)
        save_player(player)

        add_text = await event_check_and_text(player)
        if player["day_temperature"] == 4 or player["day_humidity"] == 4:
            life_ran = random.randint(0, 20)
            print(life_ran)
            if life_ran == 0:
                player['toxic_time'], player['fire_time'], player['temperature'], player['humidity'] = 0, 0, 19, 50
                player['god_blessing_time'] = player['day'] + 3

                text_god_blessing_time = player["god_blessing_time"] - player["day"]

                if text_god_blessing_time > 1:
                    dnya_day = "дні"
                elif text_god_blessing_time == 1:
                    dnya_day = "день"
                else:
                    dnya_day = "помилка #1"
                app = ('Ваш город втрачено. Ви провалили своє завдання...\n'
                       '✨Помираючи, ви бачите як з небес на вас проливається світло, Боги цього світу вирішили дати вам другий шанс.\n'
                       'Ви отримуєте ефект <b>Божественне благословення</b> на 3 дні\n\n'
                       f'Ви під дією ефекту <b>Божественне благословення</b> ще {text_god_blessing_time} {dnya_day}. '
                       f'Температура та вологість повертаються до стандартних значень')

            else:
                end_day = player['day']
                await callback_query.message.edit_text(
                    f'Ваш город втрачено. Ви провалили своє завдання...\nДень: {end_day}')
                end_game(player)
                return

        full_text = f'{text}\n{add_text}'

        await asyncio.sleep(0.7)

        await callback_query.message.edit_text(
            f'{app}{full_text}\nПотенційна кількість плодів з клітинки: {player["cell_fruits"]}.\n'
            f'Вологість дорівнює {player["humidity"]}%.\n'
            f'Температура становить {player["temperature"]}°C\n{player["size_cell"]}\n{consequences}\n'
            f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
            f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>.\n'
            f'Обери покращення для свого городу:', parse_mode=ParseMode.HTML, reply_markup=kb.upgrade)



@router.callback_query(lambda c: c.data == 'Expansion')
async def expansion(callback_query: CallbackQuery):
    if edit_lock.locked():
        await callback_query.answer("⏳ Зачекай, дію вже виконуємо...", show_alert=False)
        return
    async with edit_lock:
        await callback_query.answer()

        app = ''

        user_id = callback_query.from_user.id
        player = get_player(user_id)

        if not player:
            add_player(user_id)
            player = get_player(user_id)

        if player["size_cell"].shape[0] == 10:
            await callback_query.message.edit_text('Ваша територія закінчилась, більше розширятись не вийде. Оберіть інше покращення',
                                                   reply_markup=kb.upgrade_without_expansion)
            return

        if player["day_temperature"] == 4 or player["day_humidity"] == 4:
            life_ran = random.randint(0, 20)
            print(life_ran)
            if life_ran == 0:
                player['toxic_time'], player['fire_time'], player['temperature'], player['humidity'] = 0, 0, 19, 50
                player['god_blessing_time'] = player['day'] + 3

                text_god_blessing_time = player["god_blessing_time"] - player["day"]

                if text_god_blessing_time > 1:
                    dnya_day = "дні"
                elif text_god_blessing_time == 1:
                    dnya_day = "день"
                else:
                    dnya_day = "помилка #1"
                app = ('Ваш город втрачено. Ви провалили своє завдання...\n'
                       '✨Помираючи, ви бачите як з небес на вас проливається світло, Боги цього світу вирішили дати вам другий шанс.\n'
                       'Ви отримуєте ефект <b>Божественне благословення</b> на 3 дні\n\n'
                       f'Ви під дією ефекту <b>Божественне благословення</b> ще {text_god_blessing_time} {dnya_day}. '
                       f'Температура та вологість повертаються до стандартних значень\n\n')

            else:
                end_day = player['day']
                await callback_query.message.edit_text(f'Ваш город втрачено. Ви провалили своє завдання...\nДень: {end_day}')
                end_game(player)
                return "Ви", f"{end_day}"
        if player['late_blight_time'] > player['day']:
            pass
        else:
            player["size_cell"] -= 1

            if np.any(player["size_cell"] == 0):
                player["fruits"] += np.count_nonzero(player['size_cell'] == 0) * player['cell_fruits']
                player['fruits'] = round(player["fruits"], 0)
                player["size_cell"][player["size_cell"] == 0] = 10
        rand_num = random.randint(1, 40)
        if rand_num == 1 or rand_num == 2:
            app += '🕳Під час викопування ямок ви провалились в печеру. Ви втрачаєте один день намагаючись вибратись з неї. Ця клітинка втрачена'
            new_row = np.array([[10, 10, -10]])
            player["humidity"] -= player['minus_hum']
            player["size_cell"] += 1
        elif rand_num == 3:
            app += '🪨Ви розумієте що на цій території багато каміння. Культури будуть рости довше'
            new_row = np.array([[15, 15, 15]])
        else:
            new_row = np.array([[10, 10, 10]])
            app += ''


        player["size_cell"] = np.vstack([player["size_cell"], new_row])
        player["humidity"] -= player['minus_hum']

        player["day"] += 1

        save_player(player)

        await asyncio.sleep(0.7)

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
async def fertilization(callback_query: CallbackQuery):
    if edit_lock.locked():
        await callback_query.answer("⏳ Зачекай, дію вже виконуємо...", show_alert=False)
        return
    async with edit_lock:
        await callback_query.answer()
        user_id = callback_query.from_user.id
        player = get_player(user_id)

        if not player:
            add_player(user_id)
            player = get_player(user_id)

        app = ''
        fert_text = ""

        if player["day_temperature"] == 4 or player["day_humidity"] == 4:
            life_ran = random.randint(0, 20)
            print(life_ran)
            if life_ran == 0:
                player['toxic_time'], player['fire_time'], player['temperature'], player['humidity'] = 0, 0, 19, 50
                player['god_blessing_time'] = player['day'] + 3

                text_god_blessing_time = player["god_blessing_time"] - player["day"]

                if text_god_blessing_time > 1:
                    dnya_day = "дні"
                elif text_god_blessing_time == 1:
                    dnya_day = "день"
                else:
                    dnya_day = "помилка #1"
                app = ('Ваш город втрачено. Ви провалили своє завдання...\n'
                       '✨Помираючи, ви бачите як з небес на вас проливається світло, Боги цього світу вирішили дати вам другий шанс.\n'
                       'Ви отримуєте ефект <b>Божественне благословення</b> на 3 дні\n\n'
                       f'Ви під дією ефекту <b>Божественне благословення</b> ще {text_god_blessing_time} {dnya_day}. '
                       f'Температура та вологість повертаються до стандартних значень\n\n')

            else:
                end_day = player['day']
                await callback_query.message.edit_text(
                    f'Ваш город втрачено. Ви провалили своє завдання...\nДень: {end_day}')
                end_game(player)
                return "Ви", f"{end_day}"

        match player["fertilizer_baff"]:
            case "standart":
                player["cell_fruits"] += 1
                fert_text = 'Ти удобрив огород'
            case "freeze":
                player["cell_fruits"] += 1
                player["temperature"] -= 10
                fert_text = 'Ти удобрив огород та зменшив температуру ґрунту на 10°C'
            case "warm":
                player["cell_fruits"] += 1
                player["temperature"] += 10
                fert_text = 'Ти удобрив огород та зменшив температуру ґрунту на 10°C'
            case 'moisturizing':
                player["cell_fruits"] += 1
                player["humidity"] += 15
                fert_text = 'Ти удобрив огород та збільшив вологість ґрунту на 15%'
            case 'dry':
                player['cell_fruits'] += 1
                player['humidity'] -= 15
                fert_text = 'Ти удобрив огород та зменшив вологість ґрунту на 15%'

        if player['late_blight_time'] > player['day']:
            pass
        else:
            player["size_cell"] -= 1

            if np.any(player["size_cell"] == 0):
                player["fruits"] += np.count_nonzero(player['size_cell'] == 0) * player['cell_fruits']
                player['fruits'] = round(player["fruits"], 0)
                player["size_cell"][player["size_cell"] == 0] = 10
        player["cell_fruits"] += 1
        player["cell_fruits"] = round(player["cell_fruits"])
        player["humidity"] -= player['minus_hum']

        player["day"] += 1

        save_player(player)

        await asyncio.sleep(0.7)

        await callback_query.message.edit_text(f'{app}{fert_text}. Тепер з кожної клітинки вийде {player["cell_fruits"]} плодів.\n'
                                            f'📆День {player["day"]} закінчено.\n'
                                               f'Вологість ґрунту становить {player["humidity"]}%.\n'
                                            f'Температура {player["temperature"]}°C.\n'
                                               f'Ваша кількість плодів: {player["fruits"]}.\n'
                                               f'Розмір городу становить \n{player["size_cell"]}.\n\n'
                                               f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
                                               f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>', reply_markup=kb.next_day, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data == 'Watering')
async def watering(callback_query: CallbackQuery):
    if edit_lock.locked():
        await callback_query.answer("⏳ Зачекай, дію вже виконуємо...", show_alert=False)
        return
    async with edit_lock:
        await callback_query.answer()
        user_id = callback_query.from_user.id
        player = get_player(user_id)

        if not player:
            add_player(user_id)
            player = get_player(user_id)

        app = ''

        if player["day_temperature"] == 4 or player["day_humidity"] == 4:
            life_ran = random.randint(0, 20)
            print(life_ran)
            if life_ran == 0:
                player['toxic_time'], player['fire_time'], player['temperature'], player['humidity'] = 0, 0, 19, 50
                player['god_blessing_time'] = player['day'] + 3

                text_god_blessing_time = player["god_blessing_time"] - player["day"]

                if text_god_blessing_time > 1:
                    dnya_day = "дні"
                elif text_god_blessing_time == 1:
                    dnya_day = "день"
                else:
                    dnya_day = "помилка #1"
                app = ('Ваш город втрачено. Ви провалили своє завдання...\n'
                       '✨Помираючи, ви бачите як з небес на вас проливається світло, Боги цього світу вирішили дати вам другий шанс.\n'
                       'Ви отримуєте ефект <b>Божественне благословення</b> на 3 дні\n\n'
                       f'Ви під дією ефекту <b>Божественне благословення</b> ще {text_god_blessing_time} {dnya_day}. '
                       f'Температура та вологість повертаються до стандартних значень\n\n')

            else:
                end_day = player['day']
                await callback_query.message.edit_text(
                    f'Ваш город втрачено. Ви провалили своє завдання...\nДень: {end_day}')
                end_game(player)
                return "Ви", f"{end_day}"

        if player['late_blight_time'] > player['day']:
            pass
        else:
            player["size_cell"] -= 1

            if np.any(player["size_cell"] == 0):
                player["fruits"] += np.count_nonzero(player['size_cell'] == 0) * player['cell_fruits']
                player['fruits'] = round(player["fruits"], 0)
                player["size_cell"][player["size_cell"] == 0] = 10
        player["humidity"] += 30
        player["humidity"] -= player['minus_hum']
        player["temperature"] -= 5

        player["day"] += 1

        save_player(player)

        await asyncio.sleep(0.7)

        await callback_query.message.edit_text(f'{app}Ти полив огород. Тепер вологість ґрунту становить {player["humidity"]}%. Температура зменшена на 5°C.\n'
                                               f'📆День {player["day"]} закінчено.\n'
                                            f'Температура {player["temperature"]}°C.\n'
                                               f'З кожної клітинки вийде {player["cell_fruits"]} плодів.\n'
                                               f'Ваша кількість плодів: {player["fruits"]}.\n'
                                               f'Розмір городу: \n{player["size_cell"]}.\n\n'
                                               f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
                                               f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>', reply_markup=kb.next_day, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data == 'Hilling')
async def hilling(callback_query: CallbackQuery):
    if edit_lock.locked():
        await callback_query.answer("⏳ Зачекай, дію вже виконуємо...", show_alert=False)
        return
    async with edit_lock:
        await callback_query.answer()
        user_id = callback_query.from_user.id
        player = get_player(user_id)
        if not player:
            add_player(user_id)
            player = get_player(user_id)

        app = ''

        if player["day_temperature"] == 4 or player["day_humidity"] == 4:
            life_ran = random.randint(0, 20)
            print(life_ran)
            if life_ran == 0:
                player['toxic_time'], player['fire_time'], player['temperature'], player['humidity'] = 0, 0, 19, 50
                player['god_blessing_time'] = player['day'] + 3

                text_god_blessing_time = player["god_blessing_time"] - player["day"]

                if text_god_blessing_time > 1:
                    dnya_day = "дні"
                elif text_god_blessing_time == 1:
                    dnya_day = "день"
                else:
                    dnya_day = "помилка #1"
                app = ('Ваш город втрачено. Ви провалили своє завдання...\n'
                       '✨Помираючи, ви бачите як з небес на вас проливається світло, Боги цього світу вирішили дати вам другий шанс.\n'
                       'Ви отримуєте ефект <b>Божественне благословення</b> на 3 дні\n\n'
                       f'Ви під дією ефекту <b>Божественне благословення</b> ще {text_god_blessing_time} {dnya_day}. '
                       f'Температура та вологість повертаються до стандартних значень\n\n')


            else:
                end_day = player['day']
                await callback_query.message.edit_text(
                    f'Ваш город втрачено. Ви провалили своє завдання...\nДень: {end_day}')
                end_game(player)
                return "Ви", f"{end_day}"

        if player['late_blight_time'] > player['day']:
            pass
        else:
            player["size_cell"] -= 1

            if np.any(player["size_cell"] == 0):
                player["fruits"] += np.count_nonzero(player['size_cell'] == 0) * player['cell_fruits']
                player['fruits'] = round(player["fruits"], 0)
                player["size_cell"][player["size_cell"] == 0] = 10
        player["humidity"] -= player['minus_hum']
        player["day"] += 1
        player['temperature'] += 7
        player['humidity'] -= 10
        save_player(player)

        await asyncio.sleep(0.7)

        await callback_query.message.edit_text(
            f'{app}Ви підгорнули грядки та збільшили температуру на 7°C. Тепер температура становить {player["temperature"]}%.\n'
            f'📆День {player["day"]} закінчено.\n'
            f'Вологість дорівнює {player['humidity']}%.\n'
            f'З кожної клітинки вийде {player["cell_fruits"]} плодів.\n'
            f'Ваша кількість плодів: {player["fruits"]}.\n'
            f'Розмір городу: \n{player["size_cell"]}.\n\n'
            f'💀Очки смерті через температуру: <b>{player["day_temperature"]}</b>.\n'
            f'💀Очки смерті через вологість: <b>{player["day_humidity"]}</b>', reply_markup=kb.next_day,
            parse_mode=ParseMode.HTML)

