from django.urls import path
from chats import views

urlpatterns = [
    path('chats/', views.view_chats, name='chats'),
    path('get/chat/<int:pk>/', views.get_chat, name='get_chat'),
    path('get/messages/<int:chat_id>/', views.get_messages, name='get_messages'),
]