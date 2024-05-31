from aiogram import types, Router, F
from sqlalchemy.ext.asyncio import AsyncSession


from database import orm
from filters.chat_types import ChatTypeFilter
from keyboard.kbds import (get_attack_kb,
                           get_callback_buttons,
                           get_character_page)


do_attack_router = Router()
do_attack_router.message.filter(ChatTypeFilter(['private']))


@do_attack_router.callback_query(F.data.startswith('attack_'))
async def choose_attack(callback: types.CallbackQuery,
                        session: AsyncSession):
    await callback.answer()
    character_id = int(callback.data.split('_')[-1])

    character = await orm.orm_get_character(session, character_id=character_id)
    media = types.InputMediaPhoto(media=character.image,
                                  caption='Чем атаковать?')
    reply_markup = get_attack_kb(character.attacks)
    await callback.message.edit_media(media=media,
                                      reply_markup=reply_markup)


@do_attack_router.callback_query(F.data.startswith('do_attack_'))
async def count_attack_damage(callback: types.CallbackQuery,
                              session: AsyncSession):
    await callback.answer()
    attack_id = int(callback.data.split('_')[-1])
    attack = await orm.orm_get_attack(session, attack_id=attack_id)
    dices = await orm.orm_get_dices(session, attack_id=attack_id)
    damage_string = ''
    full_damage = 0
    for dice in dices:
        dice_damage = dice.get_damage()
        damage_string += f'D{dice.num_faces}({dice_damage}) + '
        full_damage += dice_damage
    damage_string += f'{attack.bonus} = {full_damage + attack.bonus}'

    btn = {damage_string: 'get_back'}
    await callback.message.edit_caption(
        caption='Расчет урона:',
        reply_markup=get_callback_buttons(btns=btn)
    )


@do_attack_router.callback_query(F.data.startswith('get_back'))
async def after_return(callback: types.CallbackQuery,
                       session: AsyncSession):
    user_id = callback.from_user.id
    user = await orm.orm_get_user(session, user_id=user_id)

    image, caption, reply_markup = get_character_page(user.active_character)
    media = types.InputMediaPhoto(media=image,
                                  caption=caption)
    await callback.message.edit_media(media=media,
                                      reply_markup=reply_markup)
