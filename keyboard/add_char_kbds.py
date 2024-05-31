from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Race, BattleClass
from utils.paginator import Paginator


class AddCharCallBack(CallbackData, prefix='addchar'):
    banner_name: str
    page: int = 1
    stage: int = 0
    selected_id: int | None = None
    stat_choice: int | None = None


def get_hello_btns(*, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='Давай',
        callback_data=AddCharCallBack(banner_name='name').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text='Пока не хочу',
        callback_data='skip'
    ))
    return keyboard.adjust(*sizes).as_markup()


def get_hint_btn(*, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='Введите с клавиатуры ⤵️',
        callback_data='skip'
    ))
    return keyboard.adjust(*sizes).as_markup()


def get_hint_image_btn(*, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='📎 Прикрепите картинку',
        callback_data='skip'
    ))
    return keyboard.adjust(*sizes).as_markup()


def get_stats_btns(*, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='Бросить кубики 🎲',
        callback_data=AddCharCallBack(banner_name='stats_auto').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text='Ввести значения вручную',
        callback_data=AddCharCallBack(banner_name='stats_manual').pack()
    ))
    return keyboard.adjust(*sizes).as_markup()


def get_stats_auto_btns(*, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='Распределить характеристики',
        callback_data=AddCharCallBack(banner_name='strength').pack()
    ))
    return keyboard.adjust(*sizes).as_markup()


def get_stats_finish_btns(*, sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='Продолжить',
        callback_data=AddCharCallBack(banner_name='race').pack()
    ))
    return keyboard.adjust(*sizes).as_markup()


def get_stat_btns(*,
                  next_page: str,
                  stats: tuple[int],
                  stage: int,
                  sizes: tuple[int] = (6,)):
    keyboard = InlineKeyboardBuilder()
    for stat in stats:
        keyboard.add(InlineKeyboardButton(
            text=f'{stat}',
            callback_data=AddCharCallBack(banner_name=next_page,
                                          stage=stage+1,
                                          stat_choice=stat).pack()
        ))
    return keyboard.adjust(*sizes).as_markup()


def get_finish_btns(*, sizes: tuple[int] = (2, )):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='Создать еще одного!',
        callback_data=AddCharCallBack(banner_name='name').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text='Выбрать персонажа',
        callback_data='skip'
    ))
    return keyboard.adjust(*sizes).as_markup()


def pages(paginator: Paginator, page: int, banner_name: str):
    btns = dict()
    if paginator.has_previous():
        btns['⬅️ Пред.'] = AddCharCallBack(banner_name=banner_name,
                                           page=page-1).pack()
    if paginator.has_next():
        btns['След. ➡️'] = AddCharCallBack(banner_name=banner_name,
                                           page=page+1).pack()
    return btns


def get_race_class_btns(*,
                        array: Race | BattleClass,
                        page: int,
                        next_page: str,
                        banner_name: str,
                        sizes: tuple[int] = (2,)):
    if page is None:
        page = 1
    paginator = Paginator(array, page=page, per_page=6)

    item_per_page = paginator.get_page()

    keyboard = InlineKeyboardBuilder()

    for item in item_per_page:
        keyboard.add(InlineKeyboardButton(
            text=item.name,
            callback_data=AddCharCallBack(banner_name=next_page,
                                          page=1,
                                          selected_id=item.id).pack()
        ))
    keyboard.adjust(*sizes)

    pagination_btns = pages(paginator, page, banner_name)
    row = []
    for text, callback_data in pagination_btns.items():
        if text == 'След. ➡️':
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=callback_data
            ))
        elif text == '⬅️ Пред.':
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=callback_data
            ))
    keyboard.row(*row)
    return keyboard.as_markup()
