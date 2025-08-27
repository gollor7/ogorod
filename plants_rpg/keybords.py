from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

event = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подія', callback_data='pick_event')]
])

upgrade = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Розширитись', callback_data='Expansion'),
     InlineKeyboardButton(text='Удобрення', callback_data='Fertilization')],
     [InlineKeyboardButton(text='Поливання', callback_data='Watering'),
     InlineKeyboardButton(text='Підгортання', callback_data='Hilling')]
])

upgrade_without_expansion = InlineKeyboardMarkup(inline_keyboard=[
     [InlineKeyboardButton(text='Удобрення', callback_data='Fertilization'),
     InlineKeyboardButton(text='Поливання', callback_data='Watering')],
     [InlineKeyboardButton(text='Підгортання', callback_data='Hilling')]
])

next_day = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Наступний день', callback_data='next_day')]
])



