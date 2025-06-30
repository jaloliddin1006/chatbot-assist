import logging
from aiogram import Bot
from data.config import ADMIN_ID

logger = logging.getLogger(__name__)


async def on_startup_notify(bot: Bot):
    """Bot ishga tushganda adminlarga xabar berish"""
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Bot ishga tushdi | id: {bot_info.id} | username: @{bot_info.username}")
        
        startup_message = (
            f"🚀 <b>Bot muvaffaqiyatli ishga tushdi!</b>\n\n"
            f"🤖 <b>Bot:</b> @{bot_info.username}\n"
            f"🆔 <b>ID:</b> {bot_info.id}\n"
            f"👑 <b>Admin panel:</b> /admin"
        )
        
        for admin_id in ADMIN_ID:
            try:
                await bot.send_message(int(admin_id), startup_message)
                logger.info(f"Admin {admin_id} ga startup xabar yuborildi")
            except Exception as e:
                logger.error(f"Admin {admin_id} ga xabar yuborishda xato: {e}")
                
    except Exception as e:
        logger.error(f"Startup notify xato: {e}")