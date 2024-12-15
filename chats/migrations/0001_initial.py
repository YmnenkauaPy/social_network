# Generated by Django 5.0.6 on 2024-12-15 17:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('read', models.BooleanField(default=False)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_of_message', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('people', models.ManyToManyField(related_name='people_in_chat', to=settings.AUTH_USER_MODEL)),
                ('messages', models.ManyToManyField(blank=True, null=True, related_name='messages_of_chat', to='chats.message')),
            ],
        ),
    ]
