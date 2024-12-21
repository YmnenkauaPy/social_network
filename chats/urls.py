from django.urls import path
from chats import views

urlpatterns = [
    path('chats/', views.view_chats, name='chats'),
    path('get/chat/<int:pk>/', views.get_chat, name='get_chat'),
    path('get/messages/<int:chat_id>/', views.get_messages, name='get_messages'),
    path('liked/message/<int:pk>/', views.liked_message, name='liked_message'),
    path('mark-read/<int:pk>/', views.mark_read, name='mark_read'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('delete_image/<str:folder>/<str:filename>', views.delete_image, name='delete_image'),
]