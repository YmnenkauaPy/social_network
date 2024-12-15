from django.urls import path
from chats import views

urlpatterns = [
    path('chats/', views.view_chats, name='chats'),
]