from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import path
from django.shortcuts import render
from django.db import transaction
from main.models import (
    TelegramUser,
    ChatConversation,
    ChatFeedback,
    Document
)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'first_name', 'last_name', 'phone_number', 'is_active', 'created_at')
    list_filter = ('is_active', 'language_code', 'created_at')
    search_fields = ('user_id', 'username', 'first_name', 'last_name', 'phone_number')


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_short', 'answer_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__first_name', 'user__username', 'question', 'answer')
    readonly_fields = ('created_at', 'updated_at')
    
    def question_short(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_short.short_description = "Savol"
    
    def answer_short(self, obj):
        return obj.answer[:50] + "..." if len(obj.answer) > 50 else obj.answer
    answer_short.short_description = "Javob"


@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ('conversation_user', 'conversation_question_short', 'feedback_type', 'created_at')
    list_filter = ('feedback_type', 'created_at')
    search_fields = ('conversation__user__first_name', 'conversation__question')
    readonly_fields = ('created_at', 'updated_at')
    
    def conversation_user(self, obj):
        return obj.conversation.user.full_name
    conversation_user.short_description = "Foydalanuvchi"
    
    def conversation_question_short(self, obj):
        return obj.conversation.question[:30] + "..." if len(obj.conversation.question) > 30 else obj.conversation.question
    conversation_question_short.short_description = "Savol"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'document_type', 'is_processed', 'status', 'file_size_formatted', 'created_at')
    list_filter = ('document_type', 'is_processed', 'status', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'chroma_document_ids', 'status')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'file', 'document_type', 'description')
        }),
        ('ChromaDB boshqaruvi', {
            'fields': ('is_processed',),
            'description': 'Hujjatni ChromaDB ga yuklash yoki o\'chirish uchun ushbu maydonni boshqaring'
        }),
        ('Tizim ma\'lumotlari', {
            'fields': ('status', 'file_size', 'chroma_document_ids', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['process_to_chromadb', 'remove_from_chromadb', 'bulk_process_selected']
    
    def file_size_formatted(self, obj):
        """Fayl hajmini formatlangan ko'rinishda ko'rsatish"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "Noma'lum"
    file_size_formatted.short_description = "Fayl hajmi"
    
    def process_to_chromadb(self, request, queryset):
        """Tanlangan hujjatlarni ChromaDB ga yuklash"""
        success_count = 0
        error_count = 0
        
        for document in queryset:
            try:
                if not document.is_processed:
                    document.is_processed = True
                    document.save()
                    success_count += 1
                else:
                    self.message_user(
                        request, 
                        f"'{document.name}' allaqachon yuklangan", 
                        level=messages.WARNING
                    )
            except Exception as e:
                error_count += 1
                self.message_user(
                    request, 
                    f"'{document.name}' yuklashda xatolik: {str(e)}", 
                    level=messages.ERROR
                )
        
        if success_count > 0:
            self.message_user(
                request, 
                f"{success_count} ta hujjat background da ChromaDB ga yuklanmoqda. Process holati 'Status' maydonida ko'rsatiladi.", 
                level=messages.SUCCESS
            )
            
        if error_count > 0:
            self.message_user(
                request, 
                f"{error_count} ta hujjatda xatolik ro'y berdi", 
                level=messages.ERROR
            )
    
    process_to_chromadb.short_description = "Tanlangan hujjatlarni ChromaDB ga yuklash"
    
    def remove_from_chromadb(self, request, queryset):
        """Tanlangan hujjatlarni ChromaDB dan o'chirish"""
        success_count = 0
        error_count = 0
        
        for document in queryset:
            try:
                if document.is_processed:
                    document.is_processed = False
                    document.save()
                    success_count += 1
                else:
                    self.message_user(
                        request, 
                        f"'{document.name}' allaqachon ChromaDB da yo'q", 
                        level=messages.WARNING
                    )
            except Exception as e:
                error_count += 1
                self.message_user(
                    request, 
                    f"'{document.name}' o'chirishda xatolik: {str(e)}", 
                    level=messages.ERROR
                )
        
        if success_count > 0:
            self.message_user(
                request, 
                f"{success_count} ta hujjat background da ChromaDB dan o'chirilmoqda. Process holati 'Status' maydonida ko'rsatiladi.", 
                level=messages.SUCCESS
            )
            
        if error_count > 0:
            self.message_user(
                request, 
                f"{error_count} ta hujjatda xatolik ro'y berdi", 
                level=messages.ERROR
            )
    
    remove_from_chromadb.short_description = "Tanlangan hujjatlarni ChromaDB dan o'chirish"
    
    def bulk_process_selected(self, request, queryset):
        """Ko'p hujjatlarni bir vaqtda process qilish"""
        if 'apply' in request.POST:
            action = request.POST.get('bulk_action')
            
            if action == 'add_to_chromadb':
                return self.process_to_chromadb(request, queryset)
            elif action == 'remove_from_chromadb':
                return self.remove_from_chromadb(request, queryset)
            else:
                self.message_user(request, "Noto'g'ri amal tanlandi", level=messages.ERROR)
        
        return render(request, 'admin/bulk_process_documents.html', {
            'documents': queryset,
            'action_checkbox_name': admin.ACTION_CHECKBOX_NAME,
        })
    
    bulk_process_selected.short_description = "Tanlangan hujjatlarni boshqarish"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('chromadb-status/', self.admin_site.admin_view(self.chromadb_status_view), name='document_chromadb_status'),
        ]
        return custom_urls + urls
    
    def chromadb_status_view(self, request):
        """ChromaDB holati haqida ma'lumot"""
        try:
            from core.chroma_manager import ChromaManager
            from main.enums import DocumentStatus
            
            chroma_manager = ChromaManager()
            
            collection_count = chroma_manager.get_collection_count()
            processed_docs = Document.objects.filter(is_processed=True, status=DocumentStatus.PROCESSED.value[0]).count()
            processing_docs = Document.objects.filter(status=DocumentStatus.PROCESSING.value[0]).count()
            error_docs = Document.objects.filter(status=DocumentStatus.ERROR.value[0]).count()
            total_docs = Document.objects.count()
            unprocessed_docs = Document.objects.filter(status=DocumentStatus.PENDING.value[0]).count()
            
            context = {
                'collection_count': collection_count,
                'processed_docs': processed_docs,
                'processing_docs': processing_docs,
                'error_docs': error_docs,
                'unprocessed_docs': unprocessed_docs,
                'total_docs': total_docs,
                'title': 'ChromaDB Holati'
            }
            
            return render(request, 'admin/chromadb_status.html', context)
            
        except Exception as e:
            messages.error(request, f"ChromaDB holatini olishda xatolik: {str(e)}")
            return HttpResponseRedirect('../')


# Admin sahifasiga qo'shimcha linklar qo'shish
admin.site.site_header = "RAG Chatbot Admin Panel"
admin.site.site_title = "RAG Chatbot"
admin.site.index_title = "Boshqaruv paneli"

