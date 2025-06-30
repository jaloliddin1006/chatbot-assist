from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    KeyboardButtonPollType,
    ReplyKeyboardRemove
)


# Eski keyboard - compatibility uchun
main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎁 Konkurslar"),
            KeyboardButton(text="🏆 Ballarim")
        ],
        [
            KeyboardButton(text="📊 Reytinglar"),
            KeyboardButton(text="👥 Taklif qilish")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

maxsus_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="location", request_location=True),
            KeyboardButton(text="contact", request_contact=True),
        ],
        [
            KeyboardButton(text=" poll", request_poll=KeyboardButtonPollType()),
        ],
        [
            KeyboardButton(text="Orqaga")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

rmk = ReplyKeyboardRemove()

# Chat bot uchun keyboardlar
phone_request = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📱 Telefon raqamini yuborish", request_contact=True)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Telefon raqamingizni yuboring"
)

# Chat rejimi uchun
chat_mode = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❓ Savol berish")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Savolingizni yozing..."
)

# Admin keyboards
def create_admin_reply_menu():
    """Admin uchun reply keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Statistika"),
                KeyboardButton(text="📢 Xabar yuborish")
            ],
            [
                KeyboardButton(text="🏆 G'oliblarni aniqlash"),
                KeyboardButton(text="👤 Foydalanuvchi rejimi")
            ]
        ],
        resize_keyboard=True
    )

def create_main_menu():
    """Asosiy menyu"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="❓ Savol berish")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Savolingizni yozing..."
    )

def create_back_button():
    """Orqaga tugmasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⬅️ Orqaga")
            ]
        ],
        resize_keyboard=True
    )

# Alias lar eski kodlar uchun
create_admin_menu = create_admin_reply_menu