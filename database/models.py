from random import randint

from typing import List

from sqlalchemy import (DateTime, func, BigInteger, String, Text,
                        ForeignKey, Integer, UniqueConstraint)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime,
                                              default=func.now(),
                                              onupdate=func.now())


class Banner(Base):
    __tablename__ = 'banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    def __str__(self):
        return self.name


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    active_character_id: Mapped[int] = mapped_column(
        ForeignKey('character.id', ondelete='SET NULL', use_alter=True),
        nullable=True)
    active_character: Mapped['Character'] = relationship(
        'Character',
        foreign_keys='User.active_character_id',
    )
    characters: Mapped[List['Character']] = relationship(
        'Character',
        foreign_keys='Character.user_id',
        backref='user')

    def __str__(self):
        return self.name


class Race(Base):
    __tablename__ = 'race'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    code: Mapped[str] = mapped_column(String(100), unique=True)

    def __str__(self):
        return self.name


class BattleClass(Base):
    __tablename__ = 'battle_class'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    code: Mapped[str] = mapped_column(String(100), unique=True)

    def __str__(self):
        return self.name


class Damage(Base):
    __tablename__ = 'damage'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    code: Mapped[str] = mapped_column(String(100), unique=True)

    def __str__(self):
        return self.name


class Character(Base):
    __tablename__ = 'character'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    image: Mapped[str] = mapped_column(String(150))
    current_hp: Mapped[int] = mapped_column(Integer, nullable=True)
    max_hp: Mapped[int] = mapped_column(Integer, nullable=True)
    temp_hp: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    exp: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=True)

    stats: Mapped[dict] = mapped_column(JSONB)

    attacks: Mapped[List['Attack']] = relationship(
        'Attack',
        foreign_keys='Attack.character_id',
        back_populates='character')

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.user_id', ondelete='CASCADE', use_alter=True),
        nullable=False)
    race_id: Mapped[int] = mapped_column(
        ForeignKey('race.id', ondelete='CASCADE'),
        nullable=False)
    battle_class_id: Mapped[int] = mapped_column(
        ForeignKey('battle_class.id', ondelete='CASCADE'),
        nullable=False)
    race: Mapped['Race'] = relationship(foreign_keys='Character.race_id',
                                        backref='character')
    battle_class: Mapped['BattleClass'] = relationship(
        foreign_keys='Character.battle_class_id',
        backref='character'
    )

    def __str__(self):
        return self.name


class Dice(Base):
    __tablename__ = 'dice'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    num_faces: Mapped[int] = mapped_column(Integer)

    damage_type_id: Mapped[int] = mapped_column(
        ForeignKey('damage.id', ondelete='CASCADE'),
        nullable=True)
    damage_type: Mapped['Damage'] = relationship(backref='dice')

    character_id: Mapped[int] = mapped_column(
        ForeignKey('character.id', ondelete='CASCADE'),
        nullable=True)
    attack_id: Mapped[int] = mapped_column(
        ForeignKey('attack.id', ondelete='CASCADE'),
        nullable=True)
    attack: Mapped['Attack'] = relationship(back_populates='dices')

    def get_damage(self):
        damage = randint(1, self.num_faces)
        return damage

    def __str__(self):
        return self.name


class Attack(Base):
    __tablename__ = 'attack'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    bonus: Mapped[int] = mapped_column(Integer, nullable=True)

    character_id: Mapped[int] = mapped_column(
        ForeignKey('character.id', ondelete='CASCADE'),
        nullable=False
    )
    character: Mapped['Character'] = relationship(
        foreign_keys='Attack.character_id',
        back_populates='attacks')
    dices: Mapped[List['Dice']] = relationship(
        'Dice',
        foreign_keys='Dice.attack_id',
        back_populates='attack')
    __table_args__ = (
        UniqueConstraint('character_id', 'name',
                         name='uq_character_attack_name'),
    )

    def __str__(self):
        return self.name
