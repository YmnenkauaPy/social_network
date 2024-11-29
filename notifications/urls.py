from django.urls import path
from notifications import views

urlpatterns = [
    path('notifications/<int:user_id>', views.view_notifications, name='notifications'),
]