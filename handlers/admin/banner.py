from aiogram import F, types, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import IsAdmin, ChatTypeFilter
from keyboard.kbds import cancel_kb
from database import orm


banner_router = Router()
banner_router.message.filter(ChatTypeFilter(['private']), IsAdmin())


class AddBanner(StatesGroup):
    name = State()
    image = State()
    description = State()


@banner_router.callback_query(StateFilter(None), F.data == 'add_banner')
async def add_change_banner(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        'Введите название баннера для добавления/изменения:',
        reply_markup=cancel_kb)
    await state.set_state(AddBanner.name)


@banner_router.message(StateFilter(AddBanner.name), F.text)
async def add_banner_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer('Введите текст страницы:',
                         reply_markup=cancel_kb)
    await state.set_state(AddBanner.description)


@banner_router.message(StateFilter(AddBanner.description), F.text)
async def add_banner_description(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await message.answer('Загрузите картинку:',
                         reply_markup=cancel_kb)
    await state.set_state(AddBanner.image)


@banner_router.message(StateFilter(AddBanner.image), F.photo)
async def add_banner_image(message: Message,
                           state: FSMContext,
                           session: AsyncSession):

    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()

    await orm.orm_add_change_banner(session, data=data)

    await message.answer('Баннер добавлен/изменен',
                         reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@banner_router.callback_query(F.data == 'banner_list')
async def get_banners(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    banners = await orm.orm_get_banners(session)
    for banner in banners:
        await callback.message.answer_photo(
            banner.image,
            caption=(f'<strong>{banner.name}</strong>\n'
                     f'{banner.description}')
        )
