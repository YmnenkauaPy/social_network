# Generated by Django 5.0.6 on 2025-01-03 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0014_chat_unread'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='unread',
        ),
    ]
