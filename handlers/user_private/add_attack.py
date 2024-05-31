from aiogram import types, Router, F
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession


from database import orm
from database.models import Damage
from filters.chat_types import ChatTypeFilter
from keyboard.kbds import dice_choice_kb, get_character_page
from keyboard.inline import get_paginate_btns


attack_router = Router()
attack_router.message.filter(ChatTypeFilter(['private']))


class AddAttack(StatesGroup):
    add_name = State()
    add_cubes = State()
    add_damage_type = State()
    add_bonus = State()
    for_character = None
    callback = None
    bot_message = None
    attack = None


@attack_router.callback_query(StateFilter(None),
                              F.data.startswith('add_attack_'))
async def add_attack(callback: types.CallbackQuery,
                     state: FSMContext,
                     session: AsyncSession):
    await callback.answer()

    character_id = int(callback.data.split('_')[-1])
    AddAttack.for_character = await orm.orm_get_character(
        session,
        character_id=character_id)
    await state.update_data(character_id=AddAttack.for_character.id)

    bot_message = await callback.message.answer('Введите название атаки:')
    AddAttack.callback = callback
    AddAttack.bot_message = bot_message
    await state.set_state(AddAttack.add_name)


@attack_router.message(StateFilter(AddAttack.add_name))
async def attack_name(message: types.Message,
                      state: FSMContext,
                      session: AsyncSession):

    attack_name = message.text
    await state.update_data(name=attack_name)
    data = await state.get_data()
    print(data)
    await orm.orm_add_attack(session, data=data)

    attack = await orm.orm_get_attack_by_name(session, data=data)
    AddAttack.attack = attack
    await AddAttack.bot_message.delete()
    AddAttack.bot_message = None
    await message.delete()
    media = types.InputMediaPhoto(media=AddAttack.for_character.image,
                                  caption='Выберите кубик для атаки')
    await AddAttack.callback.message.edit_media(media=media,
                                                reply_markup=dice_choice_kb)
    await state.set_state(AddAttack.add_cubes)


@attack_router.callback_query(StateFilter(AddAttack.add_cubes),
                              or_f(F.data.startswith('dice_'),
                                   F.data.startswith('page_damage_')))
async def add_dice(callback: types.CallbackQuery,
                   state: FSMContext,
                   session: AsyncSession,
                   page: int = 1):
    if callback.data.startswith('page_damage_'):
        page = int(callback.data.split('_')[-1])
    else:
        dice_faces = int(callback.data.split('_')[-1])
        await state.update_data(num_faces=dice_faces)
    await callback.answer()

    damage_types = await orm.orm_get_items(session,
                                           Class=Damage)
    media = types.InputMediaPhoto(media=AddAttack.for_character.image,
                                  caption='Выберите тип урона кубика')
    await callback.message.edit_media(
        media=media,
        reply_markup=get_paginate_btns(
            array=damage_types,
            page=page,
            field='damage',
        ))


@attack_router.callback_query(StateFilter(AddAttack.add_cubes),
                              F.data.startswith('choose_damage_'))
async def add_damage(callback: types.CallbackQuery,
                     state: FSMContext,
                     session: AsyncSession):
    await callback.answer()

    damage_id = int(callback.data.split('_')[-1])
    await state.update_data(damage_type_id=damage_id,
                            belongs_to_id=AddAttack.attack.id,
                            belongs_class='attack')
    data = await state.get_data()
    await orm.orm_add_cube(session, data=data)

    media = types.InputMediaPhoto(media=AddAttack.for_character.image,
                                  caption='Выберите кубик для атаки')
    await AddAttack.callback.message.edit_media(media=media,
                                                reply_markup=dice_choice_kb)


@attack_router.callback_query(StateFilter(AddAttack.add_cubes),
                              F.data == 'skip_dice')
async def add_bonus(callback: types.CallbackQuery,
                    state: FSMContext,
                    session: AsyncSession):
    await callback.answer()
    AddAttack.bot_message = await callback.message.answer(
        'Введите добавочное значение к урону:')
    AddAttack.callback = callback
    await state.set_state(AddAttack.add_bonus)


@attack_router.message(StateFilter(AddAttack.add_bonus))
async def commit_attack(message: types.Message,
                        state: FSMContext,
                        session: AsyncSession):
    bonus = int(message.text)
    await orm.orm_change_attack_bonus(session,
                                      attack_id=AddAttack.attack.id,
                                      bonus=bonus)
    await AddAttack.bot_message.delete()
    await message.delete()

    image, caption, reply_markup = get_character_page(AddAttack.for_character)
    media = types.InputMediaPhoto(media=image,
                                  caption=caption)
    await AddAttack.callback.answer(
        f'Атака добавлена: {AddAttack.attack.name}', show_alert=True
    )
    await AddAttack.callback.message.edit_media(media=media,
                                                reply_markup=reply_markup)

    AddAttack.for_character = None
    AddAttack.callback = None
    AddAttack.bot_message = None
    AddAttack.attack = None
    await state.clear()
