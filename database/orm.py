from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import User, Race, Character, Dice, Attack, Banner


# Работа с пользователем в базе ##############################################

async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(user_id=user_id,
                 first_name=first_name,
                 last_name=last_name,)
        )
        await session.commit()


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(
        User.user_id == user_id
    ).options(
        joinedload(User.characters),
        joinedload(User.active_character).joinedload(Character.race),
        joinedload(User.active_character).joinedload(Character.battle_class)
    )
    result = await session.execute(query)
    return result.scalar()


async def orm_set_active_character(session: AsyncSession,
                                   user_id: int,
                                   active_character_id: int):
    query = update(User).where(User.user_id == user_id).values(
        active_character_id=active_character_id
    )
    await session.execute(query)
    await session.commit()


# Админка #####################################################################

async def orm_add_new_item(session: AsyncSession,
                           Class: Race,
                           name: str,
                           code: str):
    query = select(Class).where(Class.name == name)
    result = await session.execute(query)

    if result.first():
        return False

    session.add(Class(name=name, code=code))
    await session.commit()
    return True


async def orm_get_items(session: AsyncSession, Class: Race):
    query = select(Class).order_by(Class.name)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_item(session: AsyncSession, Class: Race, item_id: int):
    query = select(Class).where(Class.id == item_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_change_item(session: AsyncSession,
                          Class: Race,
                          item_id: int,
                          name: str,
                          code: str):
    query = update(Class).where(Class.id == item_id).values(
        name=name,
        code=code
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_item(session: AsyncSession,
                          Class: Race,
                          item_id: int):
    query = delete(Class).where(Class.id == item_id)
    await session.execute(query)
    await session.commit()

# Работа с персонажами ########################################################


async def orm_add_character(session: AsyncSession, data: dict):
    character = Character(
        name=data['name'],
        image=data['image'],
        user_id=data['user_id'],
        race_id=data['race_id'],
        battle_class_id=data['class_id'],
        stats=data['stats'],
        exp=0,
        level=1
    )
    session.add(character)
    await session.commit()


async def orm_get_characters(session: AsyncSession, user_id: int):
    query = select(Character).where(
        Character.user_id == user_id
    ).order_by(Character.name)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_character(session: AsyncSession,
                            character_id: int):
    query = select(Character).where(Character.id == character_id)
    query = query.options(joinedload(Character.race),
                          joinedload(Character.battle_class),
                          joinedload(Character.attacks))
    result = await session.execute(query)
    return result.scalar()


async def orm_char_exists(session: AsyncSession,
                          name: str,
                          user_id: int):
    query = select(Character).where(Character.name == name,
                                    Character.user_id == user_id)
    result = await session.execute(query)
    if result.first():
        return True
    return False


async def orm_delete_character(session: AsyncSession,
                               character_id: int):
    query = delete(Character).where(Character.id == character_id)
    await session.execute(query)
    await session.commit()


async def orm_change_character(session: AsyncSession,
                               character_id: int,
                               data: dict):
    query = update(Character).where(Character.id == character_id).values(
        name=data['name'],
        image=data['image'],
        race_id=data['race_id'],
        battle_class_id=data['class_id']
    )
    await session.execute(query)
    await session.commit()


async def orm_change_exp(session: AsyncSession,
                         character_id: int,
                         exp: int):
    query = update(Character).where(Character.id == character_id).values(
        exp=exp
    )
    await session.execute(query)
    await session.commit()


async def orm_increase_level(session: AsyncSession,
                             character_id: int,
                             level: int):
    query = update(Character).where(Character.id == character_id).values(
        level=level
    )
    await session.execute(query)
    await session.commit()


# Работа с кубиками ###########################################################


async def orm_add_cube(session: AsyncSession,
                       data: dict):
    dice = None
    if data['belongs_class'] == 'attack':
        dice = Dice(
            num_faces=data['num_faces'],
            attack_id=data['belongs_to_id'],
            damage_type_id=data['damage_type_id']
        )
    elif data['belongs_class'] == 'character':
        dice = Dice(
            num_faces=['num_faces'],
            character_id=['belongs_to_id']
        )
    session.add(dice)
    await session.commit()


async def orm_get_dices(session: AsyncSession, attack_id: int):
    query = select(Dice).where(Dice.attack_id == attack_id)
    query = query.options(joinedload(Dice.damage_type))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_attack(session: AsyncSession,
                         data: dict):
    query = select(Attack).where(
        Attack.name == data['name'],
        Attack.character_id == data['character_id']
    )
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            Attack(
                name=data['name'],
                character_id=data['character_id']
            )
        )
        await session.commit()


async def orm_get_attack_by_name(session: AsyncSession, data: dict):
    query = select(Attack).where(
        Attack.name == data['name'],
        Attack.character_id == data['character_id']
    )
    result = await session.execute(query)
    return result.scalar()


async def orm_get_attack(session: AsyncSession, attack_id: int):
    query = select(Attack).where(
        Attack.id == attack_id
    )
    result = await session.execute(query)
    return result.scalar()


async def orm_change_attack_bonus(session: AsyncSession,
                                  attack_id: int,
                                  bonus: int):
    query = update(Attack).where(Attack.id == attack_id).values(
        bonus=bonus
    )
    await session.execute(query)
    await session.commit()


async def orm_get_attacks(session: AsyncSession, character_id: int):
    query = select(Attack).where(Attack.character_id == character_id)
    result = await session.execute(query)
    return result.scalars().all()

# Добавить/изменить баннерные картинки ########################################


async def orm_add_change_banner(session: AsyncSession, data: dict):
    query = select(Banner).where(Banner.name == data['name'])
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            Banner(name=data['name'],
                   image=data['image'],
                   description=data['description'])
        )
    else:
        query = update(Banner).where(Banner.name == data['name']).values(
            image=data['image'],
            description=data['description']
        )
        await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_banners(session: AsyncSession):
    query = select(Banner).order_by(Banner.name)
    result = await session.execute(query)
    return result.scalars().all()
