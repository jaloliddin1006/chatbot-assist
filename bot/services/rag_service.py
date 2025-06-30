"""
Bot uchun RAG Service
"""
import sys
import os
import logging

# Django src papkasini Python path ga qo'shish
bot_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(bot_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

# Django sozlamalarini o'rnatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    import django
    django.setup()
    from core.rag_service import RAGService
    RAG_AVAILABLE = True
except Exception as e:
    print(f"Django/RAG import error: {e}")
    RAG_AVAILABLE = False

logger = logging.getLogger(__name__)


class BotRAGService:
    def __init__(self):
        """Bot uchun RAG Service"""
        self.rag_service = None
        self.initialize()
    
    def initialize(self):
        """RAG Service ni ishga tushirish"""
        try:
            if not RAG_AVAILABLE:
                logger.warning("RAG Service mavjud emas")
                return
                
            groq_api_key = "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"
            
            # RAG Service o'zi default path ishlatadi
            self.rag_service = RAGService(groq_api_key=groq_api_key)
            logger.info("Bot RAG Service ishga tushirildi")
            
        except Exception as e:
            logger.error(f"Bot RAG Service ishga tushirishda xatolik: {e}")
            self.rag_service = None
    
    async def get_answer(self, question: str) -> str:
        """Savolga javob olish"""
        try:
            if not self.rag_service:
                return "Texnik muammo tufayli hozir javob berolmayman."
            
            # 70% similarity threshold (distance 0.3 = 70% similarity)
            answer = self.rag_service.get_answer(
                question=question, 
                similarity_threshold=0.7,
                n_results=5
            )
            
            return answer
            
        except Exception as e:
            logger.error(f"Bot RAG javob olishda xatolik: {e}")
            return "Texnik muammo tufayli hozir javob berolmayman. Iltimos, keyinroq urinib ko'ring."
    
    def is_ready(self) -> bool:
        """RAG Service tayyor ekanligini tekshirish"""
        return self.rag_service is not None


# Global RAG service instance
bot_rag_service = BotRAGService()
