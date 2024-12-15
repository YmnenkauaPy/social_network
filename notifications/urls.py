from django.urls import path
from notifications import views

urlpatterns = [
    path('notifications/<int:user_id>', views.view_notifications, name='notifications'),
    path('accept/friend/request/<int:new_friend>', views.accept_friend_request, name='accept_friend_request'),
    path('delete/notification/<int:pk>', views.delete_notification, name = 'delete_notification'),
    path('clear/notifications', views.clear_notifications, name='clear_notifications'),
    path('accept/<int:notification_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject/<int:notification_id>/', views.reject_friend_request, name='reject_friend_request'),

]