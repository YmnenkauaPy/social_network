from django.urls import path
from django.contrib.auth import views as auth_views
from authentication import views

urlpatterns = [
    path('', views.main, name='main'),
    path('count/unread/notifications/', views.main, name='count_unread_notifications'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]