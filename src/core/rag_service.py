"""
RAG Service - ChromaDB va Groq ni birlashtiruvchi servis
"""
import os
import logging
from typing import List, Dict, Any, Optional
from core.chroma_manager import ChromaManager
from core.groq_manager import GroqManager
from core.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, groq_api_key: str = None, chroma_persist_dir: str = "chroma_db"):
        """RAG Service yaratish"""
        self.chroma_manager = ChromaManager(persist_directory=chroma_persist_dir)
        self.groq_manager = GroqManager(api_key="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")
        self.document_processor = DocumentProcessor()
        
        logger.info("RAG Service ishga tushirildi")
    
    def process_and_store_documents(self, documents_directory: str) -> bool:
        """Hujjatlarni process qilib ChromaDB ga saqlash"""
        try:
            # Hujjatlarni process qilish
            chunks = self.document_processor.process_directory(documents_directory)
            
            if not chunks:
                logger.warning("Process qilinadigan hujjatlar topilmadi")
                return False
            
            # ChromaDB ga saqlash
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            self.chroma_manager.add_documents(texts=texts, metadatas=metadatas)
            
            logger.info(f"{len(chunks)} ta chunk ChromaDB ga saqlandi")
            return True
            
        except Exception as e:
            logger.error(f"Hujjatlarni saqlashda xatolik: {e}")
            return False
    
    def get_answer(self, question: str, similarity_threshold: float = 0.7, n_results: int = 5) -> str:
        """Savolga RAG yordamida javob berish"""
        try:
            # ChromaDB dan o'xshash hujjatlarni qidirish
            similar_docs = self.chroma_manager.search_similar(question, n_results=n_results)
            
            # Agar javob topilmasa
            # if not similar_docs or all(doc['distance'] > similarity_threshold for doc in similar_docs):
            #     return "Kechirasiz, sizning savolingizga javob berolmayman. Boshqa savol bering."
            
            # Eng yaqin hujjatlarni kontekst sifatida tayyorlash
            context_documents = []
            for doc in similar_docs:
                if doc['distance'] <= similarity_threshold:
                    context_documents.append(doc['document'])
            
            # Agar kontekst yo'q bo'lsa
            if not context_documents:
                return "Kechirasiz, sizning savolingizga javob berolmayman. Boshqa savol bering. conteks yo'q"
            
            # Groq orqali javob yaratish
            system_prompt = """Siz o'zbek tilida javob beradigan yordamchi assistentsiz. 
Berilgan kontekst ma'lumotlari asosida aniq, foydali va tushunarli javoblar bering. 
Kontekstda mavjud bo'lgan ma'lumotlarni ishlatib javob yarating.
Agar savol kontekstdagi ma'lumotlarga mos kelmasa, "Kechirasiz, sizning savolingizga javob berolmayman" deb javob bering."""
            
            answer = self.groq_manager.generate_response(
                query=question,
                context_documents=context_documents,
                system_prompt=system_prompt
            )
            
            logger.info(f"RAG javob yaratildi, {len(context_documents)} ta kontekst ishlatildi")
            return answer
            
        except Exception as e:
            logger.error(f"RAG javob yaratishda xatolik: {e}")
            return "Texnik muammo tufayli hozir javob berolmayman. Iltimos, keyinroq urinib ko'ring."
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Baza statistikasini olish"""
        try:
            count = self.chroma_manager.get_collection_count()
            return {
                'total_documents': count,
                'status': 'active' if count > 0 else 'empty'
            }
        except Exception as e:
            logger.error(f"Statistika olishda xatolik: {e}")
            return {'total_documents': 0, 'status': 'error'}
    
    def clear_database(self) -> bool:
        """Bazani tozalash"""
        try:
            self.chroma_manager.delete_collection()
            # Collection ni qayta yaratish
            self.chroma_manager.initialize()
            logger.info("Baza tozalandi")
            return True
        except Exception as e:
            logger.error(f"Bazani tozalashda xatolik: {e}")
            return False
    
    def add_single_document(self, text: str, metadata: Dict[str, Any] = None) -> bool:
        """Bitta hujjat qo'shish"""
        try:
            if metadata is None:
                metadata = {"source": "manual"}
            
            chunks = self.document_processor.chunk_text(text)
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
                metadatas.append(chunk_metadata)
            
            self.chroma_manager.add_documents(texts=chunks, metadatas=metadatas)
            
            logger.info(f"Hujjat qo'shildi: {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Hujjat qo'shishda xatolik: {e}")
            return False
    
    def search_documents(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Hujjatlarni qidirish"""
        try:
            return self.chroma_manager.search_similar(query, n_results=n_results)
        except Exception as e:
            logger.error(f"Hujjat qidirishda xatolik: {e}")
            return []
    
    def test_connection(self) -> Dict[str, bool]:
        """Barcha komponentlar connection ni tekshirish"""
        try:
            groq_status = self.groq_manager.check_connection()
            chroma_status = self.chroma_manager.get_collection_count() >= 0
            
            return {
                'groq': groq_status,
                'chroma': chroma_status,
                'overall': groq_status and chroma_status
            }
        except Exception as e:
            logger.error(f"Connection test da xatolik: {e}")
            return {'groq': False, 'chroma': False, 'overall': False}
