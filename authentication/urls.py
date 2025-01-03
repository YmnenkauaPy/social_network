from django.urls import path
from django.contrib.auth import views as auth_views
from authentication import views

urlpatterns = [
    path('', views.main, name='main'),
    path('count/unread/notifications/', views.main, name='count_unread_notifications'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('theme/<str:theme>/', views.change_theme, name='theme'),
    path('get/theme/', views.get_current_theme, name='get_current_theme'),
    path("forgot/password/", views.forgot_password, name="forgot_password"),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('reset/password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('password_reset_complete/', views.password_reset_complete, name='password_reset_complete'),
]