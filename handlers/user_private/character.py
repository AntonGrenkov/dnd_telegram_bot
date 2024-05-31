from aiogram import types, Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from common.consts import level_table
from filters.chat_types import ChatTypeFilter
from keyboard.inline import get_paginate_btns
from keyboard.kbds import cancel_kb, get_character_page
from database import orm


character_router = Router()
character_router.message.filter(ChatTypeFilter(['private']))


@character_router.message(Command('get_active'))
async def get_active(message: types.Message, session: AsyncSession):

    user_id = message.from_user.id
    user = await orm.orm_get_user(session, user_id=user_id)
    media, caption, reply_markup = get_character_page(
        character=user.active_character
    )

    await message.answer_photo(
        media,
        caption=caption,
        reply_markup=reply_markup
    )


@character_router.message(Command('active'))
async def get_characters(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    # characters = await orm.orm_get_characters(session,
    #                                           user_id=user_id)
    user = await orm.orm_get_user(session, user_id=user_id)
    characters = user.characters
    await message.answer('Ваши персонажи',
                         reply_markup=get_paginate_btns(array=characters,
                                                        page=1,
                                                        per_page=3,
                                                        field='character',
                                                        sizes=(1,)))


@character_router.callback_query(F.data.startswith('page_character_'))
async def get_characters_page(callback: types.CallbackQuery,
                              session: AsyncSession):
    await callback.answer()
    user_id = callback.from_user.id
    page = int(callback.data.split('_')[-1])
    # characters = await orm.orm_get_characters(session,
    #                                           user_id=user_id)
    user = await orm.orm_get_user(session, user_id=user_id)
    characters = user.characters
    await callback.message.edit_reply_markup(
        reply_markup=get_paginate_btns(array=characters,
                                       page=page,
                                       per_page=3,
                                       field='character',
                                       sizes=(1,))
    )


@character_router.callback_query(F.data.startswith('choose_character_'))
async def set_active_character(callback: types.CallbackQuery,
                               session: AsyncSession):
    await callback.answer()
    character_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    await orm.orm_set_active_character(session,
                                       user_id=user_id,
                                       active_character_id=character_id)
    character = await orm.orm_get_character(session, character_id=character_id)
    media, caption, reply_markup = get_character_page(character=character)
    await callback.message.answer_photo(
        media,
        caption=caption,
        reply_markup=reply_markup
    )


class AddExp(StatesGroup):
    add = State()
    char_for_add = None
    callback = None
    bot_message = None


@character_router.callback_query(StateFilter(None),
                                 F.data.startswith('add_exp_'))
async def add_exp(callback: types.CallbackQuery,
                  state: FSMContext,
                  session: AsyncSession):
    await callback.answer()

    character_id = int(callback.data.split('_')[-1])
    character = await orm.orm_get_character(session, character_id=character_id)
    AddExp.char_for_add = character

    bot_message = await callback.message.answer('Введите полученный опыт:',
                                                reply_markup=cancel_kb)
    AddExp.bot_message = bot_message

    AddExp.callback = callback

    await state.set_state(AddExp.add)


@character_router.message(StateFilter(AddExp.add), F.text)
async def add_exp_step2(message: types.Message,
                        state: FSMContext,
                        session: AsyncSession):
    adding_exp = int(message.text)
    new_exp = adding_exp + AddExp.char_for_add.exp
    AddExp.char_for_add.exp = new_exp
    await orm.orm_change_exp(session,
                             character_id=AddExp.char_for_add.id,
                             exp=new_exp)
    await AddExp.bot_message.delete()
    await message.delete()

    image, caption, reply_markup = get_character_page(AddExp.char_for_add)
    media = types.InputMediaPhoto(media=image,
                                  caption=caption)
    await AddExp.callback.message.edit_media(media=media,
                                             reply_markup=reply_markup)

    AddExp.bot_message = None
    AddExp.char_for_add = None
    AddExp.callback = None
    await state.clear()


@character_router.callback_query(F.data.startswith('incr_level_'))
async def increase_level(callback: types.CallbackQuery,
                         session: AsyncSession):
    character_id = int(callback.data.split('_')[-1])
    character = await orm.orm_get_character(session,
                                            character_id=character_id)
    if character.level == 20:
        await callback.answer()
        return
    elif character.exp > level_table[str(character.level)]:
        await callback.answer()
        character.level += 1
        await orm.orm_increase_level(session,
                                     character_id=character.id,
                                     level=character.level)
        image, caption, reply_markup = get_character_page(character)
        media = types.InputMediaPhoto(media=image,
                                      caption=caption)
        await callback.message.edit_media(media=media,
                                          reply_markup=reply_markup)
    else:
        await callback.answer('Не хватает опыта(', show_alert=True)
