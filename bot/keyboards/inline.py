from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def create_contest_menu() -> InlineKeyboardMarkup:
    """Konkurs asosiy menyusi"""
    buttons = [
        [
            InlineKeyboardButton(text="🏆 Mening ballarim", callback_data="my_points"),
            InlineKeyboardButton(text="📊 Reytinglar", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton(text="👥 Do'stlarni taklif qilish", callback_data="referral"),
            InlineKeyboardButton(text="📢 Ixtiyoriy kanallar", callback_data="optional_channels")
        ],
        [
            InlineKeyboardButton(text="ℹ️ Konkurs haqida", callback_data="contest_info")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_referral_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Taklif uchun keyboard"""
    referral_link = f"https://t.me/your_bot_username?start=ref_{user_id}"
    
    buttons = [
        [
            InlineKeyboardButton(
                text="📤 Do'stlarga yuborish", 
                url=f"https://t.me/share/url?url={referral_link}&text=🎁 Bu konkursda ishtirok eting va sovg'alar yutib oling!"
            )
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_optional_channels_keyboard(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Ixtiyoriy kanallar uchun keyboard"""
    buttons = []
    
    for channel in channels:
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 {channel['name']} (+{channel['points']} ball)", 
                callback_data=f"subscribe_optional_{channel['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_admin_menu() -> InlineKeyboardMarkup:
    """Admin panel asosiy menyusi"""
    buttons = [
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="🎁 Konkurslar", callback_data="admin_contests")
        ],
        [
            InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="🏆 G'oliblarni aniqlash", callback_data="admin_winners")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_back_button() -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
    ])


def create_feedback_keyboard(conversation_id: int) -> InlineKeyboardMarkup:
    """Feedback uchun inline keyboard"""
    buttons = [
        [
            InlineKeyboardButton(
                text="👍 Like", 
                callback_data=f"feedback_like_{conversation_id}"
            ),
            InlineKeyboardButton(
                text="👎 Dislike", 
                callback_data=f"feedback_dislike_{conversation_id}"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Eski keyboard - compatibility uchun
ssilki_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Telegram", url="https://t.me/Mamatmusayev_uz"),
            InlineKeyboardButton(text="Youtube", url="https://youtube.com/mamatmusayev.uz/")
        ],
    ]
)



