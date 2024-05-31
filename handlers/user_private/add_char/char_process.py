from aiogram.types import InputMediaPhoto, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database import orm
from database.models import Race, BattleClass
from keyboard.add_char_kbds import (
    get_hello_btns, get_hint_btn, get_race_class_btns,
    get_finish_btns, get_hint_image_btn, get_stats_btns,
    get_stats_auto_btns, get_stat_btns, get_stats_finish_btns
)
from utils.stats import get_stats_auto_result, stats_list


class AddChar(StatesGroup):
    add_name = State()
    add_image = State()
    add_stats = State()
    stat_dict = {}
    callback = None


async def hello_page(session, banner_name):
    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_hello_btns()

    return image, kbds


async def add_name_page(session, banner_name,
                        state: FSMContext,
                        callback: CallbackQuery):
    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_hint_btn()

    await state.set_state(AddChar.add_name)
    AddChar.callback = callback

    return image, kbds


async def add_race_page(session, banner_name, page):

    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    races = await orm.orm_get_items(session, Class=Race)

    kbds = get_race_class_btns(array=races,
                               page=page,
                               next_page='class',
                               banner_name=banner_name)

    return image, kbds


async def add_class_page(session, banner_name, state, page, selected_id):

    if selected_id is not None:
        await state.update_data(race_id=selected_id)

    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    classes = await orm.orm_get_items(session, Class=BattleClass)

    kbds = get_race_class_btns(array=classes,
                               page=page,
                               next_page='image',
                               banner_name=banner_name)

    return image, kbds


async def add_image_page(session, banner_name, state, callback, selected_id):

    await state.update_data(class_id=selected_id)

    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_hint_image_btn()

    await state.set_state(AddChar.add_image)
    AddChar.callback = callback

    return image, kbds


async def add_stats_page(session, banner_name):

    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_stats_btns()

    return image, kbds


async def stats_auto_page(session, banner_name, state):

    banner = await orm.orm_get_banner(session, banner_name)

    stats, caption = get_stats_auto_result()
    await state.update_data(stats=stats)

    image = InputMediaPhoto(media=banner.image, caption=caption)

    kbds = get_stats_auto_btns()

    return image, kbds


async def stats_manual_page(session, banner_name, state, callback):

    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_hint_btn()

    AddChar.callback = callback
    await state.set_state(AddChar.add_stats)
    return image, kbds


async def stat_page(session, banner_name, stat_choice, state, stage):

    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    data = await state.get_data()
    stats = data['stats']

    if stat_choice is not None:
        stat_to_remove = stat_choice
        elem = stats.index(stat_to_remove)
        new_stats = tuple(stats[:elem] + stats[elem+1:])
        AddChar.stat_dict[stats_list[stage-1]] = stat_choice
        stats = new_stats
    await state.update_data(stats=stats)
    print(AddChar.stat_dict)

    next_page = stats_list[stage + 1]

    kbds = get_stat_btns(next_page=next_page, stats=stats, stage=stage)

    return image, kbds


async def stats_error_page(session, banner_name, callback):

    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    AddChar.callback = callback
    kbds = get_hint_btn()

    return image, kbds


async def stats_finish_page(session, banner_name, stat_choice, state, stage):

    AddChar.stat_dict[stats_list[stage-1]] = stat_choice
    stats = AddChar.stat_dict
    await state.update_data(stats=stats)
    AddChar.stat_dict = {}

    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_stats_finish_btns()

    return image, kbds


async def finish_char_creation(session, banner_name, state):

    data = await state.get_data()
    await orm.orm_add_character(session, data=data)
    await state.clear()

    banner = await orm.orm_get_banner(session, banner_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_finish_btns()

    return image, kbds


async def get_addchar_content(session: AsyncSession,
                              banner_name: str,
                              state: FSMContext,
                              callback: CallbackQuery,
                              page: int | None = None,
                              stage: int = 0,
                              selected_id: int | None = None,
                              stat_choice: int | None = None):
    if banner_name == 'hello':
        return await hello_page(session=session,
                                banner_name=banner_name)
    elif banner_name in ['name', 'similar_names']:
        return await add_name_page(session=session,
                                   banner_name=banner_name,
                                   state=state,
                                   callback=callback)
    elif banner_name == 'race':
        return await add_race_page(session=session,
                                   banner_name=banner_name,
                                   page=page)
    elif banner_name == 'class':
        return await add_class_page(session=session,
                                    banner_name=banner_name,
                                    state=state,
                                    page=page,
                                    selected_id=selected_id)
    elif banner_name == 'image':
        return await add_image_page(session=session,
                                    banner_name=banner_name,
                                    state=state,
                                    callback=callback,
                                    selected_id=selected_id)
    elif banner_name == 'stats':
        return await add_stats_page(session=session,
                                    banner_name=banner_name)
    elif banner_name == 'stats_auto':
        return await stats_auto_page(session=session,
                                     banner_name=banner_name,
                                     state=state)
    elif banner_name in stats_list and banner_name != 'stats_finish':
        return await stat_page(session=session,
                               banner_name=banner_name,
                               state=state,
                               stat_choice=stat_choice,
                               stage=stage)
    elif banner_name == 'stats_manual':
        return await stats_manual_page(session=session,
                                       banner_name=banner_name,
                                       state=state,
                                       callback=callback)
    elif banner_name == 'stats_error':
        return await stats_error_page(session=session,
                                      banner_name=banner_name,
                                      callback=callback)
    elif banner_name == 'stats_finish':
        return await stats_finish_page(session=session,
                                       banner_name=banner_name,
                                       state=state,
                                       stat_choice=stat_choice,
                                       stage=stage)
    elif banner_name == 'finish':
        return await finish_char_creation(session=session,
                                          banner_name=banner_name,
                                          state=state)
