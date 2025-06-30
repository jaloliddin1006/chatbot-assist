"""
Admin panel handlers
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from keyboards.inline import create_admin_menu, create_back_button
from keyboards.reply import create_admin_menu as create_admin_reply_menu, create_main_menu
from data.config import ADMIN_ID
import logging

logger = logging.getLogger(__name__)
router = Router()


class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()
    waiting_for_bonus_points = State()
    waiting_for_user_id = State()


def is_admin(user_id: int) -> bool:
    """Admin ekanligini tekshirish"""
    return str(user_id) in ADMIN_ID


@router.message(Command("admin"))
async def cmd_admin(message: Message, db_user=None):
    """Admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqlari yo'q!")
        return
    
    try:
        
        text = "👑 <b>Admin Panel</b>\n\n"
        text += f"📊 <b>Umumiy statistika:</b>\n"
        
        
        await message.answer(
            text, 
            reply_markup=create_admin_reply_menu()
        )
        
    except Exception as e:
        logger.error(f"Admin panel xato: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(F.text == "📊 Statistika")
async def btn_admin_stats(message: Message, db_user=None):
    """Admin statistika tugmasi"""
    if not is_admin(message.from_user.id):
        return
    


@router.message(F.text == "📢 Xabar yuborish")
async def btn_admin_broadcast(message: Message, state: FSMContext, db_user=None):
    """Umumiy xabar yuborish tugmasi"""
    if not is_admin(message.from_user.id):
        return
    
    await state.set_state(AdminStates.waiting_for_broadcast_message)
    
    await message.answer(
        "📢 <b>Umumiy xabar yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni yozing:\n\n"
        "⚠️ <i>Xabar HTML formatida bo'lishi mumkin</i>\n\n"
        "Bekor qilish uchun /cancel ni bosing.",
        reply_markup=create_back_button()
    )


@router.message(StateFilter(AdminStates.waiting_for_broadcast_message))
async def process_broadcast_message(message: Message, state: FSMContext, db_user=None):
    """Umumiy xabarni qayta ishlash"""
    if not is_admin(message.from_user.id):
        return
    
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Xabar yuborish bekor qilindi.", reply_markup=create_admin_reply_menu())
        return
    
        await message.answer(result_text, reply_markup=create_admin_reply_menu())
  
@router.message(F.text == "🏆 G'oliblarni aniqlash")
async def btn_admin_winners(message: Message, db_user=None):
    """G'oliblarni aniqlash tugmasi"""
    if not is_admin(message.from_user.id):
        return
    

@router.message(F.text == "👤 Foydalanuvchi rejimi")
async def btn_user_mode(message: Message, db_user=None):
    """Foydalanuvchi rejimiga o'tish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "👤 Foydalanuvchi rejimiga o'tdingiz.\n\n"
        "/admin - Admin rejimiga qaytish",
        reply_markup=create_main_menu()
    )


# Callback handlers
@router.callback_query(F.data == "admin_stats")
async def callback_admin_stats(callback: CallbackQuery, db_user=None):
    """Admin statistika callback"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.answer()
