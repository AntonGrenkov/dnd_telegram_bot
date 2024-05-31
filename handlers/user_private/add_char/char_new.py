from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter
from keyboard.add_char_kbds import AddCharCallBack
from database import orm
from utils.stats import stats_list

from handlers.user_private.add_char.char_process import (
    AddChar, get_addchar_content
)


add_character_router = Router()
add_character_router.message.filter(ChatTypeFilter(['private']))


@add_character_router.message(CommandStart())
async def start_cmd(message: Message,
                    state: FSMContext,
                    session: AsyncSession):
    user = message.from_user
    await orm.orm_add_user(session,
                           user_id=user.id,
                           first_name=user.first_name,
                           last_name=user.last_name)
    media, reply_markup = await get_addchar_content(session,
                                                    banner_name='hello',
                                                    state=state,
                                                    callback=None)
    await message.answer_photo(media.media,
                               caption=media.caption,
                               reply_markup=reply_markup)


@add_character_router.callback_query(AddCharCallBack.filter())
async def user_menu(callback: CallbackQuery,
                    state: FSMContext,
                    callback_data: AddCharCallBack,
                    session: AsyncSession):

    media, reply_markup = await get_addchar_content(
        session,
        banner_name=callback_data.banner_name,
        callback=callback,
        state=state,
        page=callback_data.page,
        selected_id=callback_data.selected_id,
        stat_choice=callback_data.stat_choice,
        stage=callback_data.stage,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@add_character_router.message(StateFilter(AddChar.add_name), F.text)
async def get_char_name(message: Message,
                        state: FSMContext,
                        session: AsyncSession):
    await state.set_state(None)
    user_id = message.from_user.id

    name = message.text

    char_exists = await orm.orm_char_exists(
        session, name=name, user_id=user_id
    )

    if char_exists:
        banner_name = 'similar_names'
        await state.set_state(AddChar.add_name)
        await message.delete()
    else:
        banner_name = 'stats'
        await state.update_data(name=name)
        await message.delete()

    media, reply_markup = await get_addchar_content(
        session,
        banner_name=banner_name,
        callback=AddChar.callback,
        state=state
    )

    await AddChar.callback.message.edit_media(media=media,
                                              reply_markup=reply_markup)
    if not char_exists:
        AddChar.callback = None


@add_character_router.message(StateFilter(AddChar.add_image), F.photo)
async def get_char_image(message: Message,
                         state: FSMContext,
                         session: AsyncSession):
    await state.set_state(None)
    image = message.photo[-1].file_id
    user_id = message.from_user.id
    await state.update_data(image=image, user_id=user_id)
    await message.delete()
    media, reply_markup = await get_addchar_content(
        session,
        banner_name='finish',
        callback=AddChar.callback,
        state=state,
    )

    await AddChar.callback.message.edit_media(media=media,
                                              reply_markup=reply_markup)


@add_character_router.message(StateFilter(AddChar.add_stats), F.text)
async def get_char_stats(message: Message,
                         state: FSMContext,
                         session: FSMContext):

    stats_raw = tuple(map(int, message.text.split(', ')))

    banner_name = 'stats_error'

    is_valid = False
    if len(stats_raw) == 6:
        stats = {stats_list[i]: stats_raw[i] for i in range(6)}
        AddChar.stat_dict = stats
        banner_name = 'stats_finish'
        await state.set_state(None)
        is_valid = True

    await message.delete()

    media, reply_markup = await get_addchar_content(
        session,
        banner_name=banner_name,
        callback=AddChar.callback,
        state=state
    )

    await AddChar.callback.message.edit_media(media=media,
                                              reply_markup=reply_markup)
    if is_valid:
        AddChar.callback = None
