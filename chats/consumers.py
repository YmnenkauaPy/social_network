from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import Chat
from chats.utils import notify_users_about_unread
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
    def create_message(self, user, chat_id, message_content='', file_content=None, replied_to_id=None):
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
            file_content=file_content,
        )
        chat.messages.add(message)
        chat.save()
        return message

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event = text_data_json.get('event')
        chat_id = text_data_json.get('chat_id')
        chat = await database_sync_to_async(Chat.objects.get)(id=int(chat_id))
        user = self.scope['user']

        if event == 'mark_as_read':
            id = text_data_json.get('id')
            await self.mark_as_read(id)

        elif event == 'make_last_message':
            msg_id = text_data_json.get('msg_id')
            await self.make_last_message(msg_id, chat_id)

        elif event == 'send_message':
            message_content = text_data_json['message']
            replied_to_id = text_data_json.get('replied_to_id')
            file_content = text_data_json.get('file_content')
            try:
                message = await self.create_message(user, self.chat_id, message_content, file_content, replied_to_id)

                user_liked = await sync_to_async(lambda: user in message.liked.all())()
                liked = await sync_to_async(lambda: message.liked.count())()

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'send_message',
                        'id': message.id,
                        'message': message.content if message.content else '',
                        'replied_to_id': message.replied_to_id,
                        'replied_to_content': message.replied_to.content if message.replied_to else None,
                        'sent_at': message.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'sender_id': user.id,
                        'sender_name': user.username,
                        'sender_profile_pic': user.profile_picture.url,
                        'liked': int(liked),
                        'user_liked':user_liked,
                        'read':message.read,
                        'file_content': str(message.file_content) if message.file_content else None,
                    }
                )
            except Exception as e:
                print("Error creating message:", e)

        await notify_users_about_unread(chat)

    async def make_last_message(self, msg_id, chat_id):
        from .models import Chat, Message
        try:
            message = await database_sync_to_async(Message.objects.get)(id=msg_id)
            chat = await database_sync_to_async(Chat.objects.get)(id=chat_id)
            chat.last_message = message
            content = '<b>photo</b>'
            if message.content:
                content = message.content

            await database_sync_to_async(chat.save)()

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'last_message',
                    'chat_id': chat_id,
                    'msg_id':msg_id,
                    'msg_content':content,
                }
            )

        except Exception as e:
            print('Error in saving last message:', e)

    async def last_message(self, event):
        await self.send(text_data=json.dumps({
            'event': 'last_message',
            'msg_id': event['msg_id'],
            'chat_id': event['chat_id'],
            'msg_content':event['msg_content'],
        }))

    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            'event':'send_message',
            'id': event['id'],
            'content': event['message'] if event['message'] else '',
            'sent_at': event['sent_at'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_profile_pic': event['sender_profile_pic'],
            'replied_to_id': event['replied_to_id'] if event['replied_to_id'] else None,
            'replied_to_content': event['replied_to_content'] if  event['replied_to_content'] else None,
            'liked': event['liked'],
            'user_liked': event['user_liked'],
            'read':event['read'],
            'file_content':event['file_content'],
        }))

    async def mark_as_read(self, id):
        from .models import Message
        try:
            message = await database_sync_to_async(Message.objects.get)(id=id)
            message.read = True
            await database_sync_to_async(message.save)()

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'message_read',
                    'id': id,
                }
            )
        except Exception as e:
            print("Error marking message as read:", e)

    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            'event': 'message_read',
            'read': True,
            'id': event['id'],
        }))

class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "request_unread_counts":
            await self.send_unread_counts()

    async def send_unread_counts(self, chat_id=None):
        if chat_id:
            chat = await database_sync_to_async(Chat.objects.get)(id=chat_id)
            unread_counts = [{'chat_id': chat.id,'unread_count': await chat.unread_count(self.user)}]
        else:
            chats = await sync_to_async(list)(Chat.objects.filter(people=self.user))

            unread_counts = [
                {"chat_id": chat.id, "unread_count": await chat.unread_count(self.user)}
                for chat in chats
            ]

        await self.send(text_data=json.dumps({
            "type": "unread_counts",
            "data": unread_counts,
        }))

    async def update_unread_counts(self, event):
        await self.send_unread_counts(event['chat_id'])
