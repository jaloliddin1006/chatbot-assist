from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from tortoise import Tortoise
from data.config import BOT_TOKEN, DATABASE_CONFIG
from middlewares.user_middleware import UserMiddleware
from middlewares.throttling import ThrottlingMiddleware
import logging

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot va Dispatcher yaratish
bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML) 
)

dp = Dispatcher()


# Middleware-larni ro'yxatdan o'tkazish
def setup_middlewares():
    """Middleware-larni ro'yxatdan o'tkazish"""
    # Tartib muhim: UserMiddleware birinchi bo'lishi kerak
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    
    # Throttling middleware
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    dp.callback_query.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    
    
    
    logger.info("✅ Middleware-lar muvaffaqiyatli ro'yxatdan o'tkazildi")

async def init_db():
    """Database ni ishga tushirish"""
    try:
        await Tortoise.init(config=DATABASE_CONFIG)
        logger.info("✅ Tortoise ORM muvaffaqiyatli ishga tushdi")
    except Exception as e:
        logger.error(f"❌ Database ulanish xatosi: {e}")
        raise

async def close_db():
    """Database ni yopish"""
    try:
        await Tortoise.close_connections()
        logger.info("✅ Tortoise ORM yopildi")
    except Exception as e:
        logger.error(f"❌ Database yopish xatosi: {e}")
