"""
Groq API Manager for LLM functionality
"""
import os
from groq import Groq
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GroqManager:
    def __init__(self, api_key: str = None):
        """Groq API boshqaruvchisi"""
        self.api_key = api_key or "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"
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable yoki api_key parametri talab qilinadi")
        
        self.client = Groq(api_key="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")
        self.model = "llama-3.3-70b-versatile"  # Llama3 70B model
        
    def generate_response(self, query: str, context_documents: List[str] = None, 
                         system_prompt: str = None) -> str:
        """RAG yordamida javob yaratish"""
        try:
            # Default system prompt
            if system_prompt is None:
                system_prompt = """Siz o'zbek tilida javob beradigan yordamchi assistentsiz. 
Berilgan kontekst asosida aniq va foydali javoblar bering. 
Agar savol kontekstda mavjud bo'lmasa, "Kechirasiz, sizning savolingizga javob berolmayman" deb javob bering."""
            
            # Context yaratish
            context = ""
            if context_documents:
                context = "\n\nKontekst ma'lumotlari:\n"
                for i, doc in enumerate(context_documents, 1):
                    context += f"{i}. {doc}\n"
            
            # User message yaratish
            user_message = f"Savol: {query}{context}"
            
            # Groq API ga so'rov
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                model=self.model,
                max_tokens=1024,
                temperature=0.3,
                top_p=0.9,
                stream=False
            )
            
            response = chat_completion.choices[0].message.content.strip()
            logger.info(f"Groq javob yaratildi: {len(response)} belgi")
            
            return response
            
        except Exception as e:
            logger.error(f"Groq API da xatolik: {e}")
            return "Kechirasiz, texnik muammo tufayli hozir javob berolmayman. Iltimos, keyinroq urinib ko'ring."
    
    def generate_simple_response(self, query: str, system_prompt: str = None) -> str:
        """Oddiy javob yaratish (kontekstsiz)"""
        try:
            if system_prompt is None:
                system_prompt = "Siz o'zbek tilida javob beradigan yordamchi assistentsiz. Qisqa va aniq javoblar bering."
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                model=self.model,
                max_tokens=512,
                temperature=0.5,
                stream=False
            )
            
            response = chat_completion.choices[0].message.content.strip()
            return response
            
        except Exception as e:
            logger.error(f"Groq simple response da xatolik: {e}")
            return "Texnik muammo tufayli javob berolmayman."
    
    def check_connection(self) -> bool:
        """Groq API connection ni tekshirish"""
        try:
            # Test so'rovi
            self.generate_simple_response("Salom", "Test uchun 'Salom' deb javob bering.")
            return True
        except Exception as e:
            logger.error(f"Groq connection test failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Mavjud modellar ro'yxatini olish"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Modellarni olishda xatolik: {e}")
            return []
