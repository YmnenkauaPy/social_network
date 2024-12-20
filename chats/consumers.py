from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f'chat_{self.chat_id}'
 
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    @database_sync_to_async
    def create_message(self, user, chat_id, message_content, replied_to_id=None):
        from . import models
        chat = models.Chat.objects.get(id=chat_id)
        replied_to = None

        if replied_to_id:
            try:
                replied_to = models.Message.objects.get(id=replied_to_id)
            except models.Message.DoesNotExist:
                pass 

        message = models.Message.objects.create(
            sender=user,
            content=message_content,
            replied_to=replied_to,
            liked=False,
        )
        chat.messages.add(message)
        chat.save()
        return message


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        replied_to_id = text_data_json.get('replied_to_id')
        user = self.scope['user'] 

        try:
            message = await self.create_message(user, self.chat_id, message_content, replied_to_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'id': message.id,
                    'message': message.content,
                    'replied_to_id': message.replied_to_id,
                    'replied_to_content': message.replied_to.content if message.replied_to else None,
                    'sent_at': message.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'sender_id': user.id,
                    'sender_name': user.username,
                    'sender_profile_pic': user.profile_picture.url,
                    'liked':message.liked,
                    'read':message.read,
                }
            )
        except Exception as e:
            print("Error creating message:", e)

    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'content': event['message'],
            'sent_at': event['sent_at'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_profile_pic': event['sender_profile_pic'],
            'replied_to_id': event['replied_to_id'] if  event['replied_to_id'] else None,
            'replied_to_content': event['replied_to_content'] if  event['replied_to_content'] else None,
            'liked': event['liked'],
            'read':event['read'],
        }))