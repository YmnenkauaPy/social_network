from django.db import models
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'sender_of_message')
    content = models.TextField(blank=True, null=True)
    file_content = models.FileField(upload_to='media/messages_files/', blank=True, null=True)
    read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    replied_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='replies')
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, null=True, related_name = 'liked_message')

class Chat(models.Model):
    people = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name = 'people_in_chat')
    messages = models.ManyToManyField(Message, related_name='messages_of_chat', blank=True, null=True)
    last_message = models.OneToOneField(Message, on_delete=models.SET_NULL, blank=True, null=True, related_name='last_message_of_chat')

    def get_user_chat_name(self, user):
        chat_name = self.chatnames.filter(user=user).first()
        return chat_name.name

    def get_another_person(self, user):
        people = self.people.all()
        another_person = people.exclude(id=user.id)

        if another_person.exists():
            return another_person.first()

        return None

    async def unread_count(self, user):
        unread = await self.messages.filter(read=False).exclude(sender=user).acount()
        return unread

class ChatName(models.Model):
    chat = models.ForeignKey(Chat, related_name='chatnames', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chatnames', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('chat', 'user')
