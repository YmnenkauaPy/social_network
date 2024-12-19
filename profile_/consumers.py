import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import timedelta
from django.utils.timezone import now

class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return

        # Подписываемся на канал с идентификатором пользователя
        self.room_name = f"user_{self.user.id}_status"
        self.room_group_name = f"status_{self.room_name}"

        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )  

        await self.accept()

        # Отправляем сообщение, что пользователь подключился
        await self.send(text_data=json.dumps({
            'status': self.get_last_seen_text(self.user),
            'is_online': self.user.is_online,
        }))

    async def disconnect(self, close_code):
        # Убираем пользователя из группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        await self.update_user_activity()

        data = json.loads(text_data)
        
        # Отправляем обновленный статус обратно клиенту
        await self.send(text_data=json.dumps({
            'status': self.get_last_seen_text(self.user),
            'is_online': self.user.is_online,
        }))

    @database_sync_to_async
    def update_user_activity(self):
        self.user.last_activity = now()
        self.user.is_online = True
        self.user.save()

    def get_last_seen_text(self, user):
        if user.is_online:
            return "online"
        
        if not user.last_activity:
            return "Last seen: unknown" 

        time_diff = now() - user.last_activity

        if time_diff < timedelta(minutes=1):
            return "Last seen a few seconds ago"
        
        elif time_diff < timedelta(hours=1):
            minutes = time_diff.seconds // 60
            return f"Last seen {minutes} minute{'s' if minutes > 1 else ''} ago"
        
        elif time_diff < timedelta(days=1):
            hours = time_diff.seconds // 3600
            return f"Last seen {hours} hour{'s' if hours > 1 else ''} ago"
        
        elif time_diff < timedelta(days=7):
            days = time_diff.days
            return f"Last seen {days} day{'s' if days > 1 else ''} ago"
        
        elif time_diff < timedelta(days=365):
            weeks = time_diff.days // 7
            return f"Last seen {weeks} week{'s' if weeks > 1 else ''} ago"
        
        else:
            years = time_diff.days // 365
            return f"Last seen {years} year{'s' if years > 1 else ''} ago"
