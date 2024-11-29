from django.urls import path
from profile_ import views

urlpatterns = [
    path('profile/<int:user_id>', views.view_profile, name='profile'),
    path('update/profile/', views.update_profile, name='update_profile'),
    path('delete/profile/<int:user_id>', views.delete_profile, name='delete_profile'),
    path('search/for/users/', views.search_for_users, name='search_for_users'),
    path('related/users/<int:user_id>/<str:relation_type>/', views.related_users, name='related_users'),
    path('toggle/follow/user/<int:user_id>/', views.toggle_follow_user, name='follow_user'),
]