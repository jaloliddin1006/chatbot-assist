from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

from main.enums import Language

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

