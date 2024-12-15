from django.db import models
from authentication.models import CustomUser

class Notification(models.Model): #Уведомления от службы поодержки или компании будут отдельно
    receiver = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.CASCADE, related_name='receiver_of_notification') 
    sender = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.CASCADE, related_name='sender_of_notification')
    name = models.CharField(max_length=32)
    description = models.TextField()
    read = models.BooleanField(default=False)
    answer = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    