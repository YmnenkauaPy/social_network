import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"] == AnonymousUser():
            await self.close()
        else:
            self.group_name = f"user_{self.scope['user'].id}"

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

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'unread_count': event['unread_count']
        }))

    @sync_to_async
    def get_unread_notifications_count(self):
        return self.scope['user'].unread_notifications_count()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "fetch_count":
            unread_count = await self.get_unread_notifications_count()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_notification',
                    'unread_count':unread_count,
                },
            )
