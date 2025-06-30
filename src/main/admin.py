from django.contrib import admin
from main.models import (
    TelegramUser,
    ChatConversation,
    ChatFeedback
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

