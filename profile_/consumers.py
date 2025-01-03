from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from asgiref.sync import sync_to_async
from django.conf import settings
from django.apps import apps
from django.utils import timezone


class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user_id = self.scope["user"].id
            await self.update_user_status_in_db(is_online=True)
            await self.accept()
        else:
            raise DenyConnection("User not authenticated")

    async def disconnect(self, close_code):
        self.user_id = self.scope['user'].id

        await self.update_user_status_in_db(is_online=False)

    @sync_to_async
    def update_user_status_in_db(self, is_online):
        CustomUser = apps.get_model(settings.AUTH_USER_MODEL)

        profile, created = CustomUser.objects.get_or_create(id=self.user_id)

        profile.is_online = is_online
        profile.last_activity = timezone.now()
        profile.save()
