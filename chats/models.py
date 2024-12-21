from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'sender_of_message')
    content = models.TextField(blank=True, null=True)
    file_content = models.FileField(upload_to='media/messages_files/', blank=True, null=True)
    read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    replied_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='replies')
    liked = models.BooleanField(default=False)

class Chat(models.Model):
    people = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name = 'people_in_chat')
    messages = models.ManyToManyField(Message, related_name='messages_of_chat', blank=True, null=True)

    def get_user_chat_name(self, user):
        chat_name = self.chatnames.filter(user=user).first()
        return chat_name.name

    def get_another_person(self, user):
        people = self.people.all() 
        another_person = people.exclude(id=user.id)

        if another_person.exists():
            return another_person.first() 

        return None  

class ChatName(models.Model):
    chat = models.ForeignKey(Chat, related_name='chatnames', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chatnames', on_delete=models.CASCADE)
    name = models.CharField(max_length=255) 

    class Meta:
        unique_together = ('chat', 'user')
