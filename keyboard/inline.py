from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from utils.paginator import Paginator


def get_callback_buttons(*,
                         btns: dict[str, str],
                         sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


def pages(paginator: Paginator, page: int, field: str):
    btns = dict()
    if paginator.has_previous():
        btns['< Пред.'] = f'page_{field}_{page-1}'
    if paginator.has_next():
        btns['След. >'] = f'page_{field}_{page+1}'
    return btns


def get_paginate_btns(array: list,
                      page: int,
                      field: str,
                      skip: bool = False,
                      per_page: int = 6,
                      sizes: tuple = (3,),):
    if array[0].name:
        array_sorted = sorted(array, key=lambda x: x.name)
    paginator = Paginator(array_sorted, page=page, per_page=per_page)
    elems_on_page = paginator.get_page()

    keyboard = InlineKeyboardBuilder()
    for elem in elems_on_page:
        keyboard.add(InlineKeyboardButton(
            text=elem.name,
            callback_data=f'choose_{field}_{elem.id}'
            ))
    keyboard.adjust(*sizes)

    pagination_btns = pages(paginator, page=page, field=field)
    row = []
    for text, callback_data in pagination_btns.items():
        if text == 'След. >':
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=callback_data
            ))
        elif text == '< Пред.':
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=callback_data
            ))
    keyboard.row(*row)
    if skip:
        row2 = []
        row.append(InlineKeyboardButton(
            text='Пропустить',
            callback_data=f'skip_{field}'
        ))
        keyboard.row(*row2)
    return keyboard.as_markup()
