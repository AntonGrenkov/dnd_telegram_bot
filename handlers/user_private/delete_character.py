from aiogram import types, Router, F
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter
from database import orm


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


# Удаление персонажа #################################################

@user_private_router.callback_query(F.data.contains('delete_character_'))
async def delete_character(callback: types.CallbackQuery,
                           session: AsyncSession,):
    character_id = int(callback.data.split('_')[-1])
    await orm.orm_delete_character(session,
                                   character_id=character_id)
    await callback.answer(f'Персонаж с id:{character_id} удален',
                          show_alert=True)
