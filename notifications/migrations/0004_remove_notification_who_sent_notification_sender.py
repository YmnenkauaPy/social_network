# Generated by Django 5.0.6 on 2024-12-13 07:19

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_notification_who_sent_alter_notification_receiver'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='who_sent',
        ),
        migrations.AddField(
            model_name='notification',
            name='sender',
            field=models.ManyToManyField(related_name='sender_of_notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]