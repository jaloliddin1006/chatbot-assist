from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import os

from main.enums import Language, DocumentType, DocumentStatus

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

    class Meta:
        abstract = True
        ordering = ['-created_at']

class TelegramUser(BaseModel):
    user_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Username")
    first_name = models.CharField(max_length=255, verbose_name="Ism")
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Familiya")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqami")
    language_code = models.CharField(max_length=10, choices=Language.choices, verbose_name="Til kodi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Telegram foydalanuvchi"
        verbose_name_plural = "Telegram foydalanuvchilar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} ({self.user_id})"

    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name


class ChatConversation(BaseModel):
    """Chat suhbati modeli"""
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='conversations', verbose_name="Foydalanuvchi")
    question = models.TextField(verbose_name="Savol")
    answer = models.TextField(verbose_name="Javob")
    
    class Meta:
        verbose_name = "Chat suhbati"
        verbose_name_plural = "Chat suhbatlari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.question[:50]}..."


class ChatFeedback(BaseModel):
    """Chat javob baholash modeli"""
    FEEDBACK_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    
    conversation = models.OneToOneField(ChatConversation, on_delete=models.CASCADE, related_name='feedback', verbose_name="Suhbat")
    feedback_type = models.CharField(max_length=10, choices=FEEDBACK_CHOICES, verbose_name="Baholash turi")
    
    class Meta:
        verbose_name = "Chat baholash"
        verbose_name_plural = "Chat baholashlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.conversation.user.full_name} - {self.feedback_type}"


def document_upload_path(instance, filename):
    """Fayl yuklash yo'li"""
    return os.path.join('documents', filename)


class Document(BaseModel):
    """Hujjat modeli - RAG uchun fayllar"""
    name = models.CharField(max_length=255, verbose_name="Nomi")
    file = models.FileField(upload_to=document_upload_path, verbose_name="Fayl")
    document_type = models.CharField(
        max_length=10, 
        choices=DocumentType.choices, 
        verbose_name="Fayl turi"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    is_processed = models.BooleanField(default=False, verbose_name="ChromaDB ga yuklangan")
    status = models.CharField(
        max_length=20, 
        choices=DocumentStatus.choices, 
        default=DocumentStatus.PENDING.value[0],
        verbose_name="Status"
    )
    chroma_document_ids = models.JSONField(
        default=list, 
        blank=True, 
        verbose_name="ChromaDB ID lari",
        help_text="ChromaDB da saqlangan chunk ID lari"
    )
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="Fayl hajmi (bytes)")
    
    class Meta:
        verbose_name = "Hujjat"
        verbose_name_plural = "Hujjatlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Fayl tipini avtomatik aniqlash
        if self.file and not self.document_type:
            file_extension = os.path.splitext(self.file.name)[1].lower()
            if file_extension == '.pdf':
                self.document_type = DocumentType.PDF.value[0]
            elif file_extension == '.txt':
                self.document_type = DocumentType.TXT.value[0]
        
        # Fayl hajmini saqlash
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
            
        # Agar fayl o'zgargan bo'lsa, qayta process qilish uchun belgilash
        file_changed = False
        is_processed_changed = False
        
        if self.pk:
            try:
                old_doc = Document.objects.get(pk=self.pk)
                if old_doc.file != self.file:
                    self.is_processed = False
                    self.status = DocumentStatus.PENDING.value[0]
                    self.chroma_document_ids = []
                    file_changed = True
                
                # is_processed maydonining o'zgarishini tekshirish
                if old_doc.is_processed != self.is_processed:
                    is_processed_changed = True
                    
            except Document.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Background da ChromaDB ga yuklash/o'chirish
        if is_processed_changed or file_changed:
            self._handle_chromadb_sync_background()
    
    def _handle_chromadb_sync_background(self):
        """Background da ChromaDB bilan sinxronizatsiya"""
        import threading
        import logging
        
        def sync_task():
            try:
                logger = logging.getLogger(__name__)
                logger.info(f"Background sync boshlandi: {self.name}, is_processed: {self.is_processed}")
                self._handle_chromadb_sync()
                logger.info(f"Background sync yakunlandi: {self.name}")
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Background ChromaDB sinxronizatsiyasida xatolik: {e}")
                # Status ni ERROR ga o'zgartirish
                Document.objects.filter(pk=self.pk).update(
                    status=DocumentStatus.ERROR.value[0]
                )
        
        # Background thread yaratish
        thread = threading.Thread(target=sync_task, daemon=True)
        thread.start()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Background thread yaratildi: {self.name}")
    
    def _handle_chromadb_sync(self):
        """ChromaDB bilan sinxronizatsiya"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Telemetry muammosini hal qilish uchun environment variable
            import os
            os.environ['ANONYMIZED_TELEMETRY'] = 'False'
            
            logger.info(f"ChromaDB sync boshlandi: {self.name}")
            logger.info(f"is_processed: {self.is_processed}, chroma_document_ids: {self.chroma_document_ids}")
            
            from core.chroma_manager import ChromaManager
            from core.document_processor import DocumentProcessor
            
            chroma_manager = ChromaManager()
            doc_processor = DocumentProcessor()
            
            if self.is_processed and not self.chroma_document_ids:
                # ChromaDB ga yuklash
                logger.info(f"ChromaDB ga yuklash: {self.name}")
                self._add_to_chromadb(chroma_manager, doc_processor)
            elif not self.is_processed and self.chroma_document_ids:
                # ChromaDB dan o'chirish
                logger.info(f"ChromaDB dan o'chirish: {self.name}")
                self._remove_from_chromadb(chroma_manager)
            else:
                logger.info(f"Hech qanday amal bajarilmadi: {self.name}")
                
        except Exception as e:
            logger.error(f"ChromaDB sinxronizatsiyasida xatolik: {e}")
            # Database update using class method to avoid threading issues
            Document.objects.filter(pk=self.pk).update(
                status=DocumentStatus.ERROR.value[0]
            )
    
    def _add_to_chromadb(self, chroma_manager, doc_processor):
        """Hujjatni ChromaDB ga qo'shish"""
        try:
            # Status ni PROCESSING ga o'zgartirish
            Document.objects.filter(pk=self.pk).update(
                status=DocumentStatus.PROCESSING.value[0]
            )
            
            # Faylni process qilish
            chunks = doc_processor.process_file(self.file.path)
            
            if chunks:
                texts = [chunk['text'] for chunk in chunks]
                metadatas = []
                ids = []
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{self.pk}_{i}"
                    ids.append(chunk_id)
                    
                    metadata = chunk['metadata'].copy()
                    metadata.update({
                        'document_id': self.pk,
                        'document_name': self.name,
                        'description': self.description or ''
                    })
                    metadatas.append(metadata)
                
                # ChromaDB ga qo'shish
                chroma_manager.add_documents(
                    texts=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                # ID larni va statusni saqlash
                Document.objects.filter(pk=self.pk).update(
                    chroma_document_ids=ids,
                    status=DocumentStatus.PROCESSED.value[0]
                )
                
        except Exception as e:
            # Xatolik statusini saqlash
            Document.objects.filter(pk=self.pk).update(
                status=DocumentStatus.ERROR.value[0]
            )
            raise Exception(f"ChromaDB ga qo'shishda xatolik: {e}")
    
    def _remove_from_chromadb(self, chroma_manager):
        """Hujjatni ChromaDB dan o'chirish"""
        try:
            if self.chroma_document_ids:
                for doc_id in self.chroma_document_ids:
                    try:
                        chroma_manager.delete_document(doc_id)
                    except:
                        pass  # ID topilmasa, davom etish
                
                # Database ni yangilash threading issues uchun
                Document.objects.filter(pk=self.pk).update(
                    chroma_document_ids=[],
                    status=DocumentStatus.PENDING.value[0]
                )
                
        except Exception as e:
            raise Exception(f"ChromaDB dan o'chirishda xatolik: {e}")
    
    def delete(self, *args, **kwargs):
        """Hujjatni o'chirishda ChromaDB dan ham o'chirish"""
        try:
            from core.chroma_manager import ChromaManager
            if self.chroma_document_ids:
                chroma_manager = ChromaManager()
                self._remove_from_chromadb(chroma_manager)
        except:
            pass  # Xatolik bo'lsa ham o'chirishni davom ettirish
        
        super().delete(*args, **kwargs)

