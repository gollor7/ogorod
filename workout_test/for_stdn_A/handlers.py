import logging

import re

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keybords import back_to_stdn_kb

logging.basicConfig(level=logging.DEBUG)
router = Router()
import keybords as kb


static_dynamic = {
    #stdn - стато-динаміка, А - рівень складності
    "stdn_A": {"Виделка - капітанський": 1, "Підйом ластівки з однією ногою до перекладини": 1, "Підйом переворотом": 1, "Підтягування в висі з 1 ногою": 1,
                "Підтягування в ластівці з 1 ногою": 1, "Підйом ластівки до перекладини": 2, "Вихід з жабки в стійку": 2, "Вихід на одну": 2, "Друкарьска машинка": 2,
                "Вихід Семенова": 2, "Підтягування в ластівці ноги широко (>45 грудусів між ногами)": 2, "Підтягування в передньому висі ноги широко (>45 грудусів між ногами)": 2,
                "Маховий вихід в стійку": 3, "Офіцерський вихід": 3, "Крабік": 3, "Метелик": 3, "Капітанський": 3, "Рушник": 3,
                "Опускання зі стійки в горизонтальний упор": 3, "Підйом переднього вису до перекладини": 3, "Силовий вихід в стійку": 4, "Вихід на дві ": 4,
                "Вихід на дві кільця": 4, "Підйом з кута в передній вис": 4, "Іспанський вихід": 4, "Вихід принца на одну": 4, "Силовий оберт вперед в задньому упорі": 4,
                "Спічаг ноги нарізно": 4, "Рушник задній": 4, "Підйом з вису силою в передній вис": 4, "Підтягування в ластівціі ноги широко (<45 грудусів між ногами)": 4,
                "Підтягування в передньому висі ноги широко (<45 грудусів між ногами)": 4, "Калісто": 5, "Підтягування в задньому висі (середня постановка рук)": 5,
                "Царський (ангел на одну)": 5, "Підтягування в прапорі": 5, "Опускання зі стійки в горизонт ноги нарізно": 5, "Віджимання в стійці на руках": 5,
                "Перекат в прапорі": 5, "Опускання з упора під турніком в ластівку": 5, "Вихід з-під кілець": 5
                }
}

#stdn_complications = ["капітанський:17", 'Підйом з кута в передній вис:24', 'Спічаг ноги нарізно:28', 'Віджимання в стійці на руках:38']

message_plus_minus = []

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply('Вітаю в тестовому телеграм боті для підрахунку очок фрістайлу з стріт воркауту. Введіть команду /fs_calc щоб розпочати.')

@router.message(Command('fs_calc'))
async def fs_calc_start(message: Message):
    await message.reply(
        f'Інструкція для користування калькулятором:'
        f'\n1. Якщо атлет завершив комбу, натискайте кнопку "Кінець комбінації".'
        f'\n2. Після вибору елементу що виконав атлет з\'явиться додаткове меню з можливими ускладненнями, але якщо вони інсують.'
        f' Наприклад: Вихід з жабки в стійку не має ускладнень, тому меню не з\'явиться. А відтискання в стійці може бути на перекладині, тому меню з\'явиться.'
        f' Для елементу в якого є хоча б одне ускладнення висвітиться вся менюшка, а не тільки ті ускладнення які є для цього елементу.'
        f' Наприклад для капітанського буде ускладнення "хват" та "на перекладині". '
        f'В капітанському ускладнення є тільки в вигляді хвату, тому "на перекладині" потрібно ігнорувати в цьому випадку.'
        f' Якщо елемент було виконано без ускладень, просто натискаєте "Нічого".'
        f'\n3. Після закінчення фрістайлу натискайте кнопку "Кінець фрістайлу". Відбудеться підрахунок всіх балів за елементи, комбінації і т.д. (Ця версія боту рахує бали за)\n'
        f'Якщо готові можете починати обирати елемент', reply_markup=kb.instruction_kb)

def append_ids_to_names(data, start_id=1):
    result = {}
    current_id = start_id
    for group_key, items in data.items():
        result[group_key] = {}
        for name, score in items.items():
            new_name = f"{name}:{current_id}"
            result[group_key][new_name] = score
            current_id += 1
    return result, current_id

static_dynamic_updated, next_id = append_ids_to_names(static_dynamic, start_id=1)
def find_key_by_id_dict(data: dict, target_id: str) -> tuple[str, str] | None:
    for group_name, group in data.items():
        for key in group:
            if key.endswith(f":{target_id}"):
                return group_name, key
    return None


comb_dodanok = []
points_list = []
your_freestyle = []

@router.callback_query(lambda c: c.data == 'stdn_A')
async def stdn_A(callback_query: CallbackQuery):
    builder = InlineKeyboardBuilder()
    for key, values in static_dynamic_updated["stdn_A"].items():
        cb_data = f'{key.split(":")[1]}:{str(values)}'
        key_lower = key.lower()
        key_use = key.split(":")[0]
        if "вихід" in key_lower:
            key_use = '🔺' + key_use
        elif "підтягування" in key_lower:
            key_use = '🟠' + key_use
        elif "віджимання" in key_lower:
            key_use = '🔷' + key_use
        builder.button(text=key_use.split(":")[0], callback_data=cb_data)
    builder.adjust(2)

    keyboard = builder.as_markup()
    combined_kb = InlineKeyboardMarkup(inline_keyboard=keyboard.inline_keyboard + back_to_stdn_kb.inline_keyboard)
    cleaned_list = [re.sub(r':\d+', '', item).replace("'", "") for item in your_freestyle]
    result_text = '\n'.join(cleaned_list)
    await callback_query.message.edit_text(f'Виступ:\n{result_text}\n', reply_markup=combined_kb)

@router.callback_query(lambda c: ":" in c.data)
async def choose_element(callback_query: CallbackQuery):
    part1, part2 = callback_query.data.split(":", 1)
    result = find_key_by_id_dict(static_dynamic_updated, part1) #в парт1 айді елементу
    if result is None:
        await callback_query.message.answer('Невідома помилка')
        return

    group_name, found_key = result
    letter = group_name.split("_", 1)[1]
    if letter == "A":
        comb_dodanok.append("1")
    else:
        await callback_query.message.edit_text('Помилка: Елемент не належить до жодного рівня складності, не вдалося підрахувати бал за комбу')
    points_list.append(part2)
    print(points_list)  # для відладки
    your_freestyle.append(found_key)
    cleaned_list = [re.sub(r':\d+', '', item).replace("'", "") for item in your_freestyle]
    result_text = '\n'.join(cleaned_list)
    await callback_query.message.edit_text(f'Виступ: \n{result_text}', reply_markup=kb.instruction_kb)


@router.callback_query(lambda c: c.data == 'end_combination')
async def ending_comb(callback_query: CallbackQuery):
    if len(comb_dodanok) > 2:
        summary = sum(int(i) for i in comb_dodanok)
        points_list.append(summary)
    comb_dodanok.clear()
    your_freestyle.append(f"_")
    cleaned_list = [re.sub(r':\d+', '', item).replace("'", "") for item in your_freestyle]
    result_text = '\n'.join(cleaned_list)
    await callback_query.message.edit_text(f'Виступ: \n{result_text}\n', reply_markup=kb.instruction_kb)

@router.callback_query(lambda c: c.data == 'end_freestyle')
async def ending_freestyle(callback_query: CallbackQuery):
    if len(comb_dodanok) > 2:
        summary_point = sum(int(i) for i in comb_dodanok)
        points_list.append(summary_point)
    plus_minuc = sum(i for i in message_plus_minus)
    points_list.append(plus_minuc)
    summary_point = sum(int(i) for i in points_list)
    cleaned_list = [re.sub(r':\d+', '', item).replace("'", "") for item in your_freestyle]
    result_text = '\n'.join(cleaned_list)
    await callback_query.message.edit_text(f'Виступ: \n{result_text}\n\nТвої бали: {summary_point}')
    comb_dodanok.clear()
    points_list.clear()
    your_freestyle.clear()
    message_plus_minus.clear()

#@router.callback_query(lambda c: c.data in ['grip', 'on_the_bar', 'nothing'])
#async def if_map_complication(callback_query: CallbackQuery):
#    if callback_query.data == 'grip':
#        last_element = your_freestyle[-1]
#        your_freestyle[-1] = last_element + '|хват'
#        cleaned_list = [re.sub(r':\d+', '', item).replace("'", "") for item in your_freestyle]
#        result_text = '\n'.join(cleaned_list)
#        points_list.append(1)
#        await callback_query.message.edit_text(f'Виступ: \n{result_text}', reply_markup=kb.instruction_kb)
#    if callback_query.data == 'on_the_bar':
#        last_element = your_freestyle[-1]
#        your_freestyle[-1] = last_element + '|на перекладині'
#        cleaned_list = [re.sub(r':\d+', '', item).replace("'", "") for item in your_freestyle]
#        result_text = '\n'.join(cleaned_list)
#        points_list.append(3)
#        await callback_query.message.edit_text(f'Виступ: \n{result_text}', reply_markup=kb.instruction_kb)
#    if callback_query.data == 'nothing':
#        cleaned_list = [re.sub(r':\d+', '', item).replace("'", "") for item in your_freestyle]
#        result_text = '\n'.join(cleaned_list)
#        await callback_query.message.edit_text(f'Виступ: {result_text}', reply_markup=kb.instruction_kb)



@router.callback_query(lambda c: c.data == 'back_to_instruct')
async def back_to_instruct(callback_query: CallbackQuery):
    cleaned_list = [re.sub(r':\d+', '', item).replace("'", "") for item in your_freestyle]
    result_text = '\n'.join(cleaned_list)
    await callback_query.message.edit_text(f'Виступ: \n{result_text}', reply_markup=kb.instruction_kb)

@router.message()
async def message_handler(message: Message):
    if isinstance(message.text, str):
        print('Трінг')
        try:
            number = int(message.text)
            print(number)
            message_plus_minus.append(number)
            print(message_plus_minus)
            await message.answer(f'Бал за останній елемент змінено на {number}')
        except ValueError:
            print("Не число")
    else:
        print('не стрінг')

