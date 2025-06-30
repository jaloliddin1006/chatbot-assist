"""
RAG tizimini test qilish uchun management command
"""
from django.core.management.base import BaseCommand
from main.models import Document
from core.rag_service import RAGService
import logging

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'RAG tizimini test qilish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-doc',
            type=int,
            help='Test qilinadigan document ID',
        )
        parser.add_argument(
            '--test-query',
            type=str,
            help='Test savol',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='ChromaDB statistikasini ko\'rsatish',
        )

    def handle(self, *args, **options):
        if options['stats']:
            self.show_stats()
        
        if options['test_doc']:
            self.test_document(options['test_doc'])
            
        if options['test_query']:
            self.test_query(options['test_query'])

    def show_stats(self):
        """ChromaDB statistikasini ko'rsatish"""
        self.stdout.write("=== ChromaDB Statistikasi ===")
        
        try:
            rag_service = RAGService()
            stats = rag_service.get_database_stats()
            
            self.stdout.write(f"ChromaDB dagi hujjatlar soni: {stats['total_documents']}")
            self.stdout.write(f"Status: {stats['status']}")
            
            # Django DB statistikasi
            total_docs = Document.objects.count()
            processed_docs = Document.objects.filter(is_processed=True).count()
            
            self.stdout.write(f"Django DB da jami hujjatlar: {total_docs}")
            self.stdout.write(f"Process qilingan hujjatlar: {processed_docs}")
            
        except Exception as e:
            self.stdout.write(f"Xatolik: {e}")

    def test_document(self, doc_id):
        """Hujjatni test qilish"""
        self.stdout.write(f"=== Document {doc_id} ni test qilish ===")
        
        try:
            document = Document.objects.get(pk=doc_id)
            self.stdout.write(f"Nomi: {document.name}")
            self.stdout.write(f"is_processed: {document.is_processed}")
            self.stdout.write(f"Status: {document.status}")
            self.stdout.write(f"Chroma IDs: {len(document.chroma_document_ids) if document.chroma_document_ids else 0}")
            
            # Manual sync
            self.stdout.write("Manual sync boshlayapman...")
            document._handle_chromadb_sync()
            
            # Qayta yuklash
            document.refresh_from_db()
            self.stdout.write(f"Sync dan keyin status: {document.status}")
            self.stdout.write(f"Sync dan keyin Chroma IDs: {len(document.chroma_document_ids) if document.chroma_document_ids else 0}")
            
        except Document.DoesNotExist:
            self.stdout.write(f"Document {doc_id} topilmadi")
        except Exception as e:
            self.stdout.write(f"Xatolik: {e}")

    def test_query(self, query):
        """RAG query test qilish"""
        self.stdout.write(f"=== Query test: {query} ===")
        
        try:
            rag_service = RAGService()
            answer = rag_service.get_answer(query)
            
            self.stdout.write(f"Javob: {answer}")
            
        except Exception as e:
            self.stdout.write(f"Xatolik: {e}")
