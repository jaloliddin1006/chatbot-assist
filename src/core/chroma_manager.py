"""
ChromaDB Manager for RAG functionality
"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import logging
from sentence_transformers import SentenceTransformer
import uuid

# Telemetry muammosini hal qilish uchun
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

logger = logging.getLogger(__name__)


class ChromaManager:
    def __init__(self, persist_directory: str = None):
        """ChromaDB boshqaruvchisi"""
        if persist_directory is None:
            # Default path - loyiha root papkasidagi chroma_db
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            persist_directory = os.path.join(project_root, 'chroma_db')
            
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.initialize()
    
    def initialize(self):
        """ChromaDB ni ishga tushirish"""
        try:
            # Telemetry ni o'chirish
            os.environ['ANONYMIZED_TELEMETRY'] = 'False'
            
            # ChromaDB client yaratish
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Embedding model yuklash
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Collection yaratish yoki olish
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("ChromaDB muvaffaqiyatli ishga tushirildi")
            
        except Exception as e:
            logger.error(f"ChromaDB ishga tushirishda xatolik: {e}")
            raise
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None, ids: List[str] = None):
        """Hujjatlarni ChromaDB ga qo'shish"""
        try:
            if not texts:
                return
            
            # ID larni yaratish agar berilmagan bo'lsa
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in texts]
            
            # Metadata ni tekshirish
            if metadatas is None:
                metadatas = [{"source": "unknown"} for _ in texts]
            
            # Embedding yaratish
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # ChromaDB ga qo'shish
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"{len(texts)} ta hujjat ChromaDB ga qo'shildi")
            
        except Exception as e:
            logger.error(f"Hujjatlarni qo'shishda xatolik: {e}")
            raise
    
    def search_similar(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """O'xshash hujjatlarni qidirish"""
        try:
            # Query uchun embedding yaratish
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # ChromaDB dan qidirish
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Natijalarni formatlash
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Qidirishda xatolik: {e}")
            return []
    
    def delete_collection(self):
        """Collection ni o'chirish"""
        try:
            self.client.delete_collection("documents")
            logger.info("Collection o'chirildi")
        except Exception as e:
            logger.error(f"Collection o'chirishda xatolik: {e}")
    
    def get_collection_count(self) -> int:
        """Collection dagi hujjatlar sonini olish"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Count olishda xatolik: {e}")
            return 0
    
    def update_document(self, doc_id: str, text: str, metadata: Dict = None):
        """Hujjatni yangilash"""
        try:
            embedding = self.embedding_model.encode([text]).tolist()
            
            self.collection.update(
                ids=[doc_id],
                embeddings=embedding,
                documents=[text],
                metadatas=[metadata] if metadata else None
            )
            
            logger.info(f"Hujjat yangilandi: {doc_id}")
            
        except Exception as e:
            logger.error(f"Hujjatni yangilashda xatolik: {e}")
            raise
    
    def delete_document(self, doc_id: str):
        """Hujjatni o'chirish"""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Hujjat o'chirildi: {doc_id}")
        except Exception as e:
            logger.error(f"Hujjatni o'chirishda xatolik: {e}")
            raise
