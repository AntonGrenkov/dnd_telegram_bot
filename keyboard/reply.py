from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


def get_keyboard(*btns: str,
                 placeholder=None,
                 sizes: tuple[int] = (2,)):
    keyboard = ReplyKeyboardBuilder()
    for text in btns:
        keyboard.add(KeyboardButton(text=text))
    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder,
    )
