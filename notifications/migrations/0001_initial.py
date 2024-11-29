# Generated by Django 5.0.6 on 2024-11-16 09:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('description', models.TextField()),
                ('read', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SystemOfNotifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unread_count', models.PositiveIntegerField(default=0)),
                ('notifications', models.ManyToManyField(blank=True, related_name='list_of_notifications', to='notifications.notification')),
                ('receiver', models.ManyToManyField(blank=True, related_name='receivers_of_notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
