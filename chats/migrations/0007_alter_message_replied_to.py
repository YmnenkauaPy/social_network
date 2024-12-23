# Generated by Django 5.0.6 on 2024-12-20 16:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0006_alter_message_replied_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='replied_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='chats.message'),
        ),
    ]
