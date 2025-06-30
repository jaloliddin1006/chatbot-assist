"""
Django command to process documents and populate ChromaDB
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.rag_service import RAGService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'PDF va TXT fayllarni o\'qib ChromaDB ga saqlash'

    def add_arguments(self, parser):
        parser.add_argument(
            '--documents-dir',
            type=str,
            default='media/documents',
            help='Hujjatlar papkasi yo\'li (default: media/documents)'
        )
        parser.add_argument(
            '--clear-db',
            action='store_true',
            help='Bazani avval tozalash'
        )
        parser.add_argument(
            '--groq-api-key',
            type=str,
            help='Groq API key (environment variable dan olinadi agar berilmasa)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('ChromaDB populyatsiyasi boshlandi...'))
        
        try:
            # Documents directory ni tekshirish
            documents_dir = options['documents_dir']
            if not os.path.isabs(documents_dir):
                # Relative path bo'lsa, Django BASE_DIR ga nisbatan qilish
                documents_dir = os.path.join(settings.BASE_DIR, documents_dir)
            
            if not os.path.exists(documents_dir):
                self.stdout.write(
                    self.style.ERROR(f'Hujjatlar papkasi mavjud emas: {documents_dir}')
                )
                return
            
            # RAG Service yaratish
            groq_api_key = options.get('groq_api_key') or os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                self.stdout.write(
                    self.style.ERROR('GROQ_API_KEY environment variable yoki --groq-api-key parametri kerak')
                )
                return
            
            rag_service = RAGService(
                groq_api_key=groq_api_key,
                chroma_persist_dir=os.path.join(settings.BASE_DIR, 'chroma_db')
            )
            
            # Connection tekshirish
            connection_status = rag_service.test_connection()
            if not connection_status['overall']:
                self.stdout.write(
                    self.style.ERROR(f'Connection test failed: {connection_status}')
                )
                return
            
            # Bazani tozalash (agar kerak bo'lsa)
            if options['clear_db']:
                self.stdout.write('Baza tozalanmoqda...')
                if rag_service.clear_database():
                    self.stdout.write(self.style.SUCCESS('Baza tozalandi'))
                else:
                    self.stdout.write(self.style.ERROR('Bazani tozalashda xatolik'))
                    return
            
            # Hujjatlarni process qilish va saqlash
            self.stdout.write(f'Hujjatlar process qilinmoqda: {documents_dir}')
            
            if rag_service.process_and_store_documents(documents_dir):
                # Statistika
                stats = rag_service.get_database_stats()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Muvaffaqiyat! ChromaDB ga {stats["total_documents"]} ta hujjat saqlandi'
                    )
                )
                
                # Test qidirish
                self.stdout.write('Test qidirish...')
                test_results = rag_service.search_documents("test", n_results=3)
                self.stdout.write(f'Test qidirish natijalari: {len(test_results)} ta natija topildi')
                
            else:
                self.stdout.write(
                    self.style.ERROR('Hujjatlarni process qilishda xatolik yuz berdi')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Xatolik yuz berdi: {e}')
            )
            logger.error(f'ChromaDB populate command error: {e}', exc_info=True)
