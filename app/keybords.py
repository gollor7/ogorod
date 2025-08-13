from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text = "Каталог")],
    [KeyboardButton(text = "Корзина"), KeyboardButton(text = 'Контакти')]
],
resize_keyboard = True,
input_field_placeholder = 'Оберіть пункт меню')

settings = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Силка хуй пойми на шо', url='https://www.youtube.com/watch?v=qRyshRUA0xM&list=PLV0FNhq3XMOJ31X9eBWLIZJ4OVjBwb-KM&index=4&ab_channel=%24sudoteachIT%E2%9A%99%EF%B8%8F')]])



