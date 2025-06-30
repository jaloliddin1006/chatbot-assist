"""
Tortoise ORM modellari
Django main.models ga aynan mos async modellar
"""
from tortoise.models import Model
from tortoise import fields
from typing import Optional, List
from datetime import datetime
import json


class TelegramUser(Model):
    """Telegram foydalanuvchi modeli - Django TelegramUser bilan aynan bir xil"""
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(unique=True, description="Telegram ID")
    username = fields.CharField(max_length=255, null=True, description="Username")
    first_name = fields.CharField(max_length=255, description="Ism")
    last_name = fields.CharField(max_length=255, null=True, description="Familiya")
    phone_number = fields.CharField(max_length=20, null=True, description="Telefon raqami")
    language_code = fields.CharField(max_length=10, null=True, description="Til kodi")
    is_active = fields.BooleanField(default=True, description="Faol")
    created_at = fields.DatetimeField(auto_now_add=True, description="Yaratilgan sana")
    updated_at = fields.DatetimeField(auto_now=True, description="Yangilangan sana")

    class Meta:
        table = "main_telegramuser"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} ({self.user_id})"

    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name


class ChatConversation(Model):
    """Chat suhbati modeli - Django ChatConversation bilan aynan bir xil"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.TelegramUser', related_name='conversations', description="Foydalanuvchi")
    question = fields.TextField(description="Savol")
    answer = fields.TextField(description="Javob")
    created_at = fields.DatetimeField(auto_now_add=True, description="Yaratilgan sana")
    updated_at = fields.DatetimeField(auto_now=True, description="Yangilangan sana")

    class Meta:
        table = "main_chatconversation"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.first_name} - {self.question[:50]}..."


class ChatFeedback(Model):
    """Chat javob baholash modeli - Django ChatFeedback bilan aynan bir xil"""
    id = fields.IntField(pk=True)
    conversation = fields.OneToOneField('models.ChatConversation', related_name='feedback', description="Suhbat")
    feedback_type = fields.CharField(max_length=10, description="Baholash turi")  # 'like' yoki 'dislike'
    created_at = fields.DatetimeField(auto_now_add=True, description="Yaratilgan sana")
    updated_at = fields.DatetimeField(auto_now=True, description="Yangilangan sana")

    class Meta:
        table = "main_chatfeedback"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.conversation.user.first_name} - {self.feedback_type}"

