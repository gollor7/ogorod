from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

instruction_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Статодинаміка рівень А', callback_data='stdn_A')],
    [InlineKeyboardButton(text='Кінець комбінації', callback_data='end_combination'),
     InlineKeyboardButton(text='Кінець виступу', callback_data='end_freestyle')]
])

back_to_stdn_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back_to_instruct')]
])

complication = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Хват', callback_data='grip'),
     InlineKeyboardButton(text='На перекладині', callback_data='on_the_bar')],
    [InlineKeyboardButton(text='Нічого', callback_data='nothing')]
])