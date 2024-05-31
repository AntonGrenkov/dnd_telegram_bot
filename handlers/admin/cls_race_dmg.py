from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Race, BattleClass, Damage
from filters.chat_types import IsAdmin, ChatTypeFilter
from keyboard.kbds import cancel_kb, admin_kb
from keyboard.inline import get_callback_buttons
from database import orm


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())


@admin_router.message(Command('admin'))
async def show_admin_commands(message: types.Message, state: FSMContext):

    await state.clear()

    await message.answer('Что хотите сделать?',
                         reply_markup=admin_kb)


# Работа с расами #############################################################

class AddRace(StatesGroup):
    add = State()
    race_for_change = None


# добавление новой расы: 1 этап
@admin_router.callback_query(StateFilter(None), F.data == 'add_new_race')
async def new_race(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        ('Введите названия и коды рас как в примере:\n\n'
         'Гоблин: goblin\n'
         'Гном: gnome\n'
         'Дварф: dwarf'),
        reply_markup=cancel_kb
    )
    await state.set_state(AddRace.add)


@admin_router.callback_query(StateFilter(None),
                             F.data.startswith('change_race_'))
async def change_race(callback: types.CallbackQuery,
                      state: FSMContext,
                      session: AsyncSession):
    await callback.answer()
    race_id = callback.data.split('_')[-1]
    race = await orm.orm_get_item(session, Class=Race, item_id=int(race_id))
    AddRace.race_for_change = race
    await callback.message.answer(
        f'Раса:\n'
        f'<strong>{race.name}: {race.code}</strong>\n'
        f'Введите изменения:',
        reply_markup=cancel_kb
    )
    await state.set_state(AddRace.add)


@admin_router.callback_query(StateFilter(None),
                             F.data.startswith('delete_race_'))
async def delete_race(callback: types.CallbackQuery,
                      session: AsyncSession):
    race_id = callback.data.split('_')[-1]
    await orm.orm_delete_item(session,
                              Class=Race,
                              item_id=int(race_id))
    await callback.answer('Раса удалена', show_alert=True)


# добавление новой расы: отправка в базу
@admin_router.message(StateFilter(AddRace.add),
                      or_f(F.text.contains(':'),
                           F.text.lower() == 'отмена'))
async def add_race(message: types.Message,
                   state: FSMContext,
                   session: AsyncSession):
    if message.text.lower() == 'отмена':
        await message.answer('Действие отменено',
                             reply_markup=types.ReplyKeyboardRemove())
    else:
        if AddRace.race_for_change:
            name, code = message.text.split(':')
            await orm.orm_change_item(session,
                                      Class=Race,
                                      item_id=AddRace.race_for_change.id,
                                      name=name.strip(),
                                      code=code.strip().lower())
            updated_race = await orm.orm_get_item(
                session,
                Class=Race,
                item_id=AddRace.race_for_change.id
            )
            await message.answer(f'Раса {updated_race.name} изменена',
                                 reply_markup=types.ReplyKeyboardRemove())
        else:
            new_races = []
            already_exist = []
            for line in message.text.split('\n'):
                name, code = line.split(':')
                is_new = await orm.orm_add_new_item(session,
                                                    Class=Race,
                                                    name=name.strip(),
                                                    code=code.strip().lower())
                if is_new:
                    new_races.append(name.strip())
                else:
                    already_exist.append(name.strip())
            await message.answer(f'Новые расы добавлены:\n'
                                 f'{", ".join(new_races)}\n'
                                 f'Эти расы уже в системе:\n'
                                 f'{", ".join(already_exist)}',
                                 reply_markup=types.ReplyKeyboardRemove())
    AddRace.race_for_change = None
    await state.clear()


# список рас
@admin_router.callback_query(F.data == 'race_list')
async def show_race_list(callback: types.CallbackQuery, session: AsyncSession):
    callback.answer()
    races = await orm.orm_get_items(session, Class=Race)
    for race in races:
        await callback.message.answer(
            f'{race.name}({race.code})',
            reply_markup=get_callback_buttons(btns={
                    'Изменить': f'change_race_{race.id}',
                    'Удалить': f'delete_race_{race.id}'},
            )
        )


# Работа с классами ###########################################################

class AddClass(StatesGroup):
    add = State()
    class_for_change = None


# добавление нового класса: 1 этап
@admin_router.callback_query(StateFilter(None), F.data == 'add_new_class')
async def new_class(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        ('Введите названия и коды классов как в примере:\n\n'
         'Бард: bard\n'
         'Монах: monk\n'
         'Воин: fighter'),
        reply_markup=cancel_kb
    )
    await state.set_state(AddClass.add)


@admin_router.callback_query(StateFilter(None),
                             F.data.startswith('change_class_'))
async def change_class(callback: types.CallbackQuery,
                       state: FSMContext,
                       session: AsyncSession):
    await callback.answer()
    class_id = callback.data.split('_')[-1]
    battle_class = await orm.orm_get_item(session,
                                          Class=BattleClass,
                                          item_id=int(class_id))
    AddClass.class_for_change = battle_class
    await callback.message.answer(
        f'Класс:\n'
        f'<strong>{battle_class.name}: {battle_class.code}</strong>\n'
        f'Введите изменения:',
        reply_markup=cancel_kb
    )
    await state.set_state(AddClass.add)


@admin_router.callback_query(StateFilter(None),
                             F.data.startswith('delete_class_'))
async def delete_class(callback: types.CallbackQuery,
                       session: AsyncSession):
    class_id = callback.data.split('_')[-1]
    await orm.orm_delete_item(session,
                              Class=BattleClass,
                              item_id=int(class_id))
    await callback.answer('Класс удален', show_alert=True)


# добавление нового класса: отправка в базу
@admin_router.message(StateFilter(AddClass.add),
                      or_f(F.text.contains(':'),
                           F.text.lower() == 'отмена'))
async def add_class(message: types.Message,
                    state: FSMContext,
                    session: AsyncSession):
    if message.text.lower() == 'отмена':
        await message.answer('Действие отменено',
                             reply_markup=types.ReplyKeyboardRemove())
    else:
        if AddClass.class_for_change:
            name, code = message.text.split(':')
            await orm.orm_change_item(session,
                                      Class=BattleClass,
                                      item_id=AddClass.class_for_change.id,
                                      name=name.strip(),
                                      code=code.strip().lower())
            updated_class = await orm.orm_get_item(
                session,
                Class=BattleClass,
                item_id=AddClass.class_for_change.id
            )
            await message.answer(f'Класс {updated_class.name} изменен',
                                 reply_markup=types.ReplyKeyboardRemove())
        else:
            new_classes = []
            already_exist = []
            for line in message.text.split('\n'):
                name, code = line.split(':')
                is_new = await orm.orm_add_new_item(session,
                                                    Class=BattleClass,
                                                    name=name.strip(),
                                                    code=code.strip().lower())
                if is_new:
                    new_classes.append(name.strip())
                else:
                    already_exist.append(name.strip())
            await message.answer(f'Новые классы добавлены:\n'
                                 f'{", ".join(new_classes)}\n'
                                 f'Эти классы уже в системе:\n'
                                 f'{", ".join(already_exist)}',
                                 reply_markup=types.ReplyKeyboardRemove())
    AddClass.class_for_change = None
    await state.clear()


# список классов
@admin_router.callback_query(F.data == 'class_list')
async def show_class_list(callback: types.CallbackQuery,
                          session: AsyncSession):
    callback.answer()
    classes = await orm.orm_get_items(session, Class=BattleClass)
    for clas in classes:
        await callback.message.answer(
            f'{clas.name}({clas.code})',
            reply_markup=get_callback_buttons(btns={
                    'Изменить': f'change_class_{clas.id}',
                    'Удалить': f'delete_class_{clas.id}'},
            )
        )


# Работа с видом урона ########################################################

class AddDamage(StatesGroup):
    add = State()
    damage_for_change = None


# добавление нового вида урона: 1 этап
@admin_router.callback_query(StateFilter(None), F.data == 'add_new_damage')
async def new_damage(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        ('Введите виды и коды урона как в примере:\n\n'
         'Колющий: piercing\n'
         'Рубящий: slashing\n'
         'Дробящий: crushing'),
        reply_markup=cancel_kb
    )
    await state.set_state(AddDamage.add)


@admin_router.callback_query(StateFilter(None),
                             F.data.startswith('change_damage_'))
async def change_damage(callback: types.CallbackQuery,
                        state: FSMContext,
                        session: AsyncSession):
    await callback.answer()
    damage_id = callback.data.split('_')[-1]
    damage = await orm.orm_get_item(session,
                                    Class=Damage,
                                    item_id=int(damage_id))
    AddDamage.damage_for_change = damage
    await callback.message.answer(
        f'Вид урона:\n'
        f'<strong>{damage.name}: {damage.code}</strong>\n'
        f'Введите изменения:',
        reply_markup=cancel_kb
    )
    await state.set_state(AddDamage.add)


@admin_router.callback_query(StateFilter(None),
                             F.data.startswith('delete_damage_'))
async def delete_damage(callback: types.CallbackQuery,
                        session: AsyncSession):
    damage_id = callback.data.split('_')[-1]
    await orm.orm_delete_item(session,
                              Class=Damage,
                              item_id=int(damage_id))
    await callback.answer('Вид урона удален', show_alert=True)


# добавление нового вида урона: отправка в базу
@admin_router.message(StateFilter(AddDamage.add),
                      or_f(F.text.contains(':'),
                           F.text.lower() == 'отмена'))
async def add_damage(message: types.Message,
                     state: FSMContext,
                     session: AsyncSession):
    if message.text.lower() == 'отмена':
        await message.answer('Действие отменено',
                             reply_markup=types.ReplyKeyboardRemove())
    else:
        if AddDamage.damage_for_change:
            name, code = message.text.split(':')
            await orm.orm_change_item(session,
                                      Class=Damage,
                                      item_id=AddDamage.damage_for_change.id,
                                      name=name.strip(),
                                      code=code.strip().lower())
            updated_damage = await orm.orm_get_item(
                session,
                Class=Damage,
                item_id=AddDamage.damage_for_change.id
            )
            await message.answer(f'Вид урона {updated_damage.name} изменен',
                                 reply_markup=types.ReplyKeyboardRemove())
        else:
            new_classes = []
            already_exist = []
            for line in message.text.split('\n'):
                name, code = line.split(':')
                is_new = await orm.orm_add_new_item(session,
                                                    Class=Damage,
                                                    name=name.strip(),
                                                    code=code.strip().lower())
                if is_new:
                    new_classes.append(name.strip())
                else:
                    already_exist.append(name.strip())
            await message.answer(f'Новые виды урона добавлены:\n'
                                 f'{", ".join(new_classes)}\n'
                                 f'Эти виды урона уже в системе:\n'
                                 f'{", ".join(already_exist)}',
                                 reply_markup=types.ReplyKeyboardRemove())
    AddDamage.damage_for_change = None
    await state.clear()


# список классов
@admin_router.callback_query(F.data == 'damage_list')
async def show_damage_list(callback: types.CallbackQuery,
                           session: AsyncSession):
    callback.answer()
    damages = await orm.orm_get_items(session, Class=Damage)
    for damage in damages:
        await callback.message.answer(
            f'{damage.name}({damage.code})',
            reply_markup=get_callback_buttons(btns={
                    'Изменить': f'change_damage_{damage.id}',
                    'Удалить': f'delete_damage_{damage.id}'},
            )
        )
