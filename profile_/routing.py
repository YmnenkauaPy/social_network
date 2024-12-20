from django.urls import path
from .consumers import UserStatusConsumer

websocket_urlpatterns = [
    path('ws/user_status/<int:user_id>/', UserStatusConsumer.as_asgi()),
]
