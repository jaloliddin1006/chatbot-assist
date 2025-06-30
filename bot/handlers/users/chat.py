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
                language_code=user.language_code or 'uz'
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
        user = message.from_user
        contact = message.contact
        
        # Foydalanuvchini topish va telefon raqamini yangilash
        db_user = await TelegramUser.filter(user_id=user.id).first()
        if db_user:
            db_user.phone_number = contact.phone_number
            await db_user.save()
            
            await message.answer(
                f"✅ Rahmat! Telefon raqamingiz saqlandi.\n\n"
                "🤖 Endi savolingizni bering:",
                reply_markup=reply.chat_mode
            )
            await state.set_state(ChatStates.waiting_for_question)
        else:
            await message.answer("Xatolik yuz berdi. Iltimos, /start ni bosing.")
            
    except Exception as e:
        logger.error(f"Phone process error: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(ChatStates.waiting_for_phone)
async def wrong_phone_format(message: Message):
    """Noto'g'ri telefon format"""
    await message.answer(
        "📱 Telefon raqamini yuborish uchun pastdagi tugmani bosing:",
        reply_markup=reply.phone_request
    )


@router.message(ChatStates.waiting_for_question, F.text)
async def process_question(message: Message, state: FSMContext):
    """Savolni qabul qilish va javob berish"""
    try:
        user = message.from_user
        question = message.text
        
        # Typing action
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        
        # RAG service orqali javob olish
        answer = bot_rag_service.get_answer(question, similarity_threshold=0.3, n_results=5)
        
        # Foydalanuvchini topish
        db_user = await TelegramUser.filter(user_id=user.id).first()
        if not db_user:
            await message.answer("Xatolik yuz berdi. Iltimos, /start ni bosing.")
            return
        
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
            "📝 Javob sifatini baholang:",
            reply_markup=inline.create_feedback_keyboard(conversation.id)
        )
        
    except Exception as e:
        logger.error(f"Question process error: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.callback_query(F.data.startswith("feedback_"))
async def process_feedback(callback: CallbackQuery):
    """Feedback ni qabul qilish"""
    try:
        # Callback data dan ma'lumotlarni ajratish
        data_parts = callback.data.split("_")
        feedback_type = data_parts[1]  # like yoki dislike
        conversation_id = int(data_parts[2])
        
        # Conversation topish
        conversation = await ChatConversation.filter(id=conversation_id).first()
        if not conversation:
            await callback.answer("Xatolik yuz berdi.", show_alert=True)
            return
        
        # Feedback mavjudligini tekshirish
        existing_feedback = await ChatFeedback.filter(conversation=conversation).first()
        if existing_feedback:
            await callback.answer("Siz allaqachon baholagansiz.", show_alert=True)
            return
        
        # Yangi feedback yaratish
        await ChatFeedback.create(
            conversation=conversation,
            feedback_type=feedback_type
        )
        
        # Javob berish
        feedback_text = "👍 Like" if feedback_type == "like" else "👎 Dislike"
        await callback.message.edit_text(
            f"📝 Javob sifatini baholang:\n\n✅ {feedback_text} tanlandi"
        )
        
        await callback.answer("Feedbackingiz uchun rahmat!", show_alert=False)
        
        # Yangi savol so'rash
        await callback.message.answer(
            "❓ Boshqa savolingiz bormi?",
            reply_markup=reply.chat_mode
        )
        
    except Exception as e:
        logger.error(f"Feedback process error: {e}")
        await callback.answer("Xatolik yuz berdi.", show_alert=True)


@router.message(ChatStates.waiting_for_question)
async def handle_non_text_in_question_state(message: Message):
    """Savol kutilganda matn bo'lmagan xabarlar"""
    await message.answer(
        "📝 Iltimos, savolingizni matn ko'rinishida yuboring:",
        reply_markup=reply.chat_mode
    )
