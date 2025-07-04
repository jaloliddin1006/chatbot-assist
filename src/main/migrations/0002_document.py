# Generated by Django 5.2.3 on 2025-06-30 21:02

import main.enums
import main.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan sana')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan sana')),
                ('name', models.CharField(max_length=255, verbose_name='Nomi')),
                ('file', models.FileField(upload_to=main.models.document_upload_path, verbose_name='Fayl')),
                ('document_type', models.CharField(choices=main.enums.DocumentType.choices, max_length=10, verbose_name='Fayl turi')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Tavsif')),
                ('is_processed', models.BooleanField(default=False, verbose_name='ChromaDB ga yuklangan')),
                ('status', models.CharField(choices=main.enums.DocumentStatus.choices, default='pending', max_length=20, verbose_name='Status')),
                ('chroma_document_ids', models.JSONField(blank=True, default=list, help_text='ChromaDB da saqlangan chunk ID lari', verbose_name='ChromaDB ID lari')),
                ('file_size', models.PositiveIntegerField(blank=True, null=True, verbose_name='Fayl hajmi (bytes)')),
            ],
            options={
                'verbose_name': 'Hujjat',
                'verbose_name_plural': 'Hujjatlar',
                'ordering': ['-created_at'],
            },
        ),
    ]
