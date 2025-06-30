import asyncio
import signal
from handlers import bot_messages, user_commands, questionaire, admin
from handlers.users import start as user_start, chat
from callbaks import pagination
from middlewares.throttling import ThrottlingMiddleware
from utils.bot_stop import on_shutdown_notify
from utils.set_bot_commands import (
    set_private_default_commands, 
    set_adminstrators_defoult_commands,
    set_group_defoult_commands
)
from utils.bot_start import on_startup_notify
from loader import bot, dp, init_db


async def main():
    await init_db()  

    dp.message.middleware(ThrottlingMiddleware())

    dp.include_routers(
        admin.router,
        user_start.router,
        chat.router,
        user_commands.router,
        questionaire.router,
        pagination.router,
        bot_messages.router
    )

    await set_private_default_commands(bot)
    await on_startup_notify(bot)

    await bot.delete_webhook(drop_pending_updates=False)

    try:
        await dp.start_polling(bot, skip_updates=True)
    except asyncio.CancelledError:
        pass
    finally:
        await on_shutdown_notify(bot)  

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🚀 Bot o‘chirildi.")
