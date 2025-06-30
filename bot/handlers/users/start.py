from aiogram import Router, F
from aiogram.types import Message, Contact, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from filters import IsPrivateChat
from keyboards import reply, inline
from utils.states import ChatStates
from utils.db.models import TelegramUser, ChatConversation, ChatFeedback
from services.rag_service import bot_rag_service
import logging

logger = logging.getLogger(__name__)
router = Router()
router.message.filter(IsPrivateChat())


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """Start komandasi - foydalanuvchini ro'yxatdan o'tkazish"""
    try:
        user = message.from_user
        
        # Foydalanuvchi bazada bor-yo'qligini tekshirish
        db_user = await TelegramUser.filter(user_id=user.id).first()
        
        if not db_user:
            # Yangi foydalanuvchi yaratish
            db_user = await TelegramUser.create(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code
            )
            
            await message.answer(
                f"👋 Salom {user.first_name}!\n\n"
                "Men sizga turli savollaringizga javob beradigan AI assistentman.\n\n"
                "Boshlash uchun telefon raqamingizni yuboring:",
                reply_markup=reply.phone_request
            )
            await state.set_state(ChatStates.waiting_for_phone)
        else:
            # Mavjud foydalanuvchi
            if db_user.phone_number:
                await message.answer(
                    f"👋 Qaytganingiz bilan, {user.first_name}!\n\n"
                    "🤖 Savolingizni bering, men sizga yordam beraman:",
                    reply_markup=reply.chat_mode
                )
                await state.set_state(ChatStates.waiting_for_question)
            else:
                await message.answer(
                    "Telefon raqamingizni yuboring:",
                    reply_markup=reply.phone_request
                )
                await state.set_state(ChatStates.waiting_for_phone)
                
    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(ChatStates.waiting_for_phone, F.contact)
async def process_phone_number(message: Message, state: FSMContext):
    """Telefon raqamini qabul qilish"""
    try:
        contact: Contact = message.contact
        
        # Foydalanuvchini yangilash
        await TelegramUser.filter(user_id=message.from_user.id).update(
            phone_number=contact.phone_number
        )
        
        await message.answer(
            "✅ Telefon raqamingiz saqlandi!\n\n"
            "🤖 Endi savolingizni bering, men sizga yordam beraman:",
            reply_markup=reply.chat_mode
        )
        await state.set_state(ChatStates.waiting_for_question)
        
    except Exception as e:
        logger.error(f"Phone processing error: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(ChatStates.waiting_for_phone)
async def phone_number_invalid(message: Message):
    """Noto'g'ri telefon raqami"""
    await message.answer(
        "❌ Iltimos, telefon raqamingizni tugma orqali yuboring:",
        reply_markup=reply.phone_request
    )


@router.message(ChatStates.waiting_for_question)
@router.message(F.text)
async def process_question(message: Message, state: FSMContext):
    """Savol va javobni qayta ishlash"""
    try:
        # Foydalanuvchini olish
        db_user = await TelegramUser.filter(user_id=message.from_user.id).first()
        
        if not db_user:
            await message.answer("Iltimos, /start ni bosing.")
            return
        
        if not db_user.phone_number:
            await message.answer(
                "Avval telefon raqamingizni yuboring:",
                reply_markup=reply.phone_request
            )
            await state.set_state(ChatStates.waiting_for_phone)
            return
        
        question = message.text.strip()
        
        if len(question) < 3:
            await message.answer("❌ Savolingiz juda qisqa. Iltimos, batafsil yozing.")
            return
        
        # "Yozmoqda..." ko'rsatish
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        
        # RAG orqali javob olish
        if not bot_rag_service.is_ready():
            answer = "Kechirasiz, texnik muammo tufayli hozir javob berolmayman. Iltimos, keyinroq urinib ko'ring."
        else:
            answer = await bot_rag_service.get_answer(question)
        
        # Suhbatni bazaga saqlash
        conversation = await ChatConversation.create(
            user=db_user,
            question=question,
            answer=answer
        )
        
        # Javobni yuborish
        await message.answer(answer)
        
        # Feedback so'rash
        await message.answer(
            "📊 Javob sifatini baholang:",
            reply_markup=inline.create_feedback_keyboard(conversation.id)
        )
        
        # State ni qayta o'rnatish
        await state.set_state(ChatStates.waiting_for_question)
        
    except Exception as e:
        logger.error(f"Question processing error: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.callback_query(F.data.startswith("feedback_"))
async def process_feedback(callback: CallbackQuery):
    """Feedback callback ni qayta ishlash"""
    try:
        # Callback data ni parse qilish
        data_parts = callback.data.split("_")
        feedback_type = data_parts[1]  # 'like' yoki 'dislike'
        conversation_id = int(data_parts[2])
        
        # Suhbatni topish
        conversation = await ChatConversation.filter(id=conversation_id).first()
        
        if not conversation:
            await callback.answer("❌ Suhbat topilmadi!", show_alert=True)
            return
        
        # Mavjud feedback ni tekshirish
        existing_feedback = await ChatFeedback.filter(conversation=conversation).first()
        
        if existing_feedback:
            # Mavjud feedback ni yangilash
            existing_feedback.feedback_type = feedback_type
            await existing_feedback.save()
        else:
            # Yangi feedback yaratish
            await ChatFeedback.create(
                conversation=conversation,
                feedback_type=feedback_type
            )
        
        # Feedback emoji
        emoji = "👍" if feedback_type == "like" else "👎"
        feedback_text = "yoqdi" if feedback_type == "like" else "yoqmadi"
        
        await callback.answer(f"{emoji} Feedbackingiz uchun rahmat!")
        
        # Xabarni yangilash
        await callback.message.edit_text(
            f"✅ Sizga javob {feedback_text}.\n\n"
            "🤖 Yana savol bering:"
        )
        
    except Exception as e:
        logger.error(f"Feedback processing error: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)