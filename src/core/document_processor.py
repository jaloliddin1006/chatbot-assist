"""
Document processor for PDF and TXT files
"""
import os
import PyPDF2
from typing import List, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Hujjat processoeri"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF fayldan matn chiqarish"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                logger.info(f"PDF matn chiqarildi: {pdf_path}")
                return text.strip()
                
        except Exception as e:
            logger.error(f"PDF o'qishda xatolik {pdf_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, txt_path: str) -> str:
        """TXT fayldan matn chiqarish"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                text = file.read()
                
            logger.info(f"TXT matn chiqarildi: {txt_path}")
            return text.strip()
            
        except UnicodeDecodeError:
            # UTF-8 ishlamasa, boshqa encoding bilan urinish
            try:
                with open(txt_path, 'r', encoding='cp1251') as file:
                    text = file.read()
                    
                logger.info(f"TXT matn chiqarildi (cp1251): {txt_path}")
                return text.strip()
                
            except Exception as e:
                logger.error(f"TXT o'qishda xatolik {txt_path}: {e}")
                return ""
                
        except Exception as e:
            logger.error(f"TXT o'qishda xatolik {txt_path}: {e}")
            return ""
    
    def chunk_text(self, text: str) -> List[str]:
        """Matnni chunklarga bo'lish"""
        if not text:
            return []
        
        chunks = []
        words = text.split()
        
        if len(words) <= self.chunk_size:
            return [text]
        
        i = 0
        while i < len(words):
            # Chunk olish
            end_idx = min(i + self.chunk_size, len(words))
            chunk_words = words[i:end_idx]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
            
            # Overlap bilan keyingi chunk boshlanishi
            i += self.chunk_size - self.chunk_overlap
        
        logger.info(f"Matn {len(chunks)} ta chunkga bo'lingan")
        return chunks
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Fayl ni process qilish va chunk qilish"""
        try:
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()
            
            # Matn chiqarish
            text = ""
            if file_extension == '.pdf':
                text = self.extract_text_from_pdf(str(file_path))
            elif file_extension == '.txt':
                text = self.extract_text_from_txt(str(file_path))
            else:
                logger.warning(f"Qo'llab-quvvatlanmaydigan fayl turi: {file_extension}")
                return []
            
            if not text:
                logger.warning(f"Fayldan matn chiqarilmadi: {file_path}")
                return []
            
            # Chunklarga bo'lish
            chunks = self.chunk_text(text)
            
            # Metadata bilan qaytarish
            results = []
            for i, chunk in enumerate(chunks):
                results.append({
                    'text': chunk,
                    'metadata': {
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'file_extension': file_extension
                    }
                })
            
            logger.info(f"Fayl muvaffaqiyatli process qilindi: {file_path} ({len(results)} chunks)")
            return results
            
        except Exception as e:
            logger.error(f"Faylni process qilishda xatolik {file_path}: {e}")
            return []
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Papkadagi barcha PDF va TXT fayllarni process qilish"""
        try:
            directory_path = Path(directory_path)
            if not directory_path.exists():
                logger.error(f"Papka mavjud emas: {directory_path}")
                return []
            
            all_chunks = []
            
            # PDF va TXT fayllarni topish
            for file_pattern in ['*.pdf', '*.txt']:
                for file_path in directory_path.rglob(file_pattern):
                    chunks = self.process_file(str(file_path))
                    all_chunks.extend(chunks)
            
            logger.info(f"Papka muvaffaqiyatli process qilindi: {directory_path} ({len(all_chunks)} chunks)")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Papkani process qilishda xatolik {directory_path}: {e}")
            return []
