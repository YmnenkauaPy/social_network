from django.db import models
from authentication.models import CustomUser

class Notification(models.Model):
    receiver = models.ManyToManyField(CustomUser, related_name='receivers_of_notification') 
    sender = models.ManyToManyField(CustomUser, related_name='sender_of_notifications')
    name = models.CharField(max_length=32)
    description = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    