# Generated by Django 5.0.6 on 2024-12-16 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
