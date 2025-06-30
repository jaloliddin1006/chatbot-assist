from aiogram import types, Bot
from aiogram.methods import SetMyCommands
from data.config import ADMIN_ID


async def set_bot_commands(bot: Bot):
    """Barcha bot commandalarini sozlash"""
    
    # Oddiy foydalanuvchilar uchun
    user_commands = [
        types.BotCommand(command="start", description="🚀 Botni ishga tushirish"),
        types.BotCommand(command="contests", description="🎁 Faol konkurslar"),
        types.BotCommand(command="help", description="ℹ️ Yordam olish"),
    ]
    
    # Admin foydalanuvchilar uchun 
    admin_commands = user_commands + [
        types.BotCommand(command="admin", description="👑 Admin panel"),
    ]
    
    # Barcha private chatlar uchun user commands
    await bot(SetMyCommands(
        commands=user_commands, 
        scope=types.BotCommandScopeAllPrivateChats()
    ))
    
    # Admin lar uchun alohida commands
    for admin_id in ADMIN_ID:
        try:
            await bot(SetMyCommands(
                commands=admin_commands,
                scope=types.BotCommandScopeChat(chat_id=int(admin_id))
            ))
        except Exception as e:
            print(f"Admin {admin_id} uchun command o'rnatishda xato: {e}")
    
    # Guruhlar uchun
    group_commands = [
        types.BotCommand(command="start", description="🚀 Botni guruhda ishga tushirish"),
        types.BotCommand(command="help", description="ℹ️ Guruhdan yordam olish"),
    ]
    
    await bot(SetMyCommands(
        commands=group_commands,
        scope=types.BotCommandScopeAllGroupChats()
    ))


# Eski funksiyalar - compatibility uchun
async def set_private_default_commands(bot):
    """Eski funksiya - yangi set_bot_commands ishlatiladi"""
    await set_bot_commands(bot)


async def set_group_defoult_commands(bot):
    """Eski funksiya - yangi set_bot_commands ishlatiladi"""
    pass


async def set_adminstrators_defoult_commands(bot):
    """Eski funksiya - yangi set_bot_commands ishlatiladi"""
    pass