from django.urls import path
from profile_ import views

urlpatterns = [
    path('/profile/<int:user_id>', views.view_profile, name='profile'),
    path('/update_profile/', views.update_profile, name='update_profile'),
    path('/delete_profile/<int:user_id>', views.delete_profile, name='delete_profile'),
]