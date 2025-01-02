# Generated by Django 5.0.6 on 2024-12-27 19:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0010_chat_last_message'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='liked',
        ),
        migrations.AddField(
            model_name='message',
            name='liked',
            field=models.ManyToManyField(related_name='liked_message', to=settings.AUTH_USER_MODEL),
        ),
    ]