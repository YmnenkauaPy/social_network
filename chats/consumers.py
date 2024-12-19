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
    def create_message(self, user, chat_id, message_content):
        from . import models
        chat = models.Chat.objects.get(id=chat_id)
        message = models.Message.objects.create(sender=user, content=message_content)
        chat.messages.add(message)
        chat.save()
        return message

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        user = self.scope['user'] 

        try:
            message = await self.create_message(user, self.chat_id, message_content)

            # Отправляем сообщение в WebSocket группу
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'id': message.id,
                    'message': message.content,
                    'sent_at': message.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'sender_id': user.id,
                    'sender_name':user.username,
                    'sender_profile_pic':user.profile_picture.url,
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
        }))