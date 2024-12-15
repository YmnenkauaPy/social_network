from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'sender_of_message')
    content = models.TextField()
    read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
class Chat(models.Model):
    people = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name = 'people_in_chat')

    messages = models.ManyToManyField(Message, related_name='messages_of_chat', blank=True, null=True)

    def get_other_person_name(self, user):
        other_people = self.people.exclude(id=user.id)
        if other_people.exists():
            return other_people.first().username  
        return "Unknown"
