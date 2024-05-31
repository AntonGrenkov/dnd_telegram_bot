import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from dotenv import find_dotenv, load_dotenv

from administration.admins_list import admins_list
from common.bot_commands import private
from database.engine import create_db, drop_db, session_maker
from handlers.user_private.character import character_router
from handlers.user_private.add_attack import attack_router
from handlers.user_private.add_char.char_new import add_character_router
from handlers.user_private.attack import do_attack_router
from handlers.user_private.delete_character import user_private_router
from handlers.admin.cls_race_dmg import admin_router
from handlers.admin.banner import banner_router
from middleware.db import DataBaseSession

load_dotenv(find_dotenv())


bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
bot.my_admins_list = admins_list


dp = Dispatcher()

dp.include_routers(
    admin_router,
    banner_router,
    character_router,
    add_character_router,
    user_private_router,
    attack_router,
    do_attack_router,
)


async def on_startup(bot):
    drop = False
    if drop:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('Бот закончил работу')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)

    # await bot.delete_my_commands(
    #     scope=types.BotCommandScopeAllPrivateChats()
    # )

    await bot.set_my_commands(
        commands=private,
        scope=types.BotCommandScopeAllPrivateChats()
    )

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())
