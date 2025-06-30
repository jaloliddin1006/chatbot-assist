import logging
from aiogram import Bot
from data.config import ADMIN_ID

logger = logging.getLogger(__name__)


async def on_shutdown_notify(bot: Bot):
    """Bot to'xtatilganda bajariladigan funksiya"""
    try:
        shutdown_message = (
            "🛑 <b>Bot to'xtatildi!</b>\n\n"
            "🔧 Texnik ishlar yoki yangilanish amalga oshirilmoqda.\n"
            "Tez orada qayta ishga tushadi."
        )
        
        for admin_id in ADMIN_ID:
            try:
                await bot.send_message(int(admin_id), shutdown_message)
                logger.info(f"Admin {admin_id} ga shutdown xabar yuborildi")
            except Exception as e:
                logger.error(f"Admin {admin_id} ga shutdown xabar yuborishda xato: {e}")
        
        logger.info("✅ Bot to'xtatildi")
        
    except Exception as e:
        logger.error(f"Shutdown notify xato: {e}")
