from django.urls import path
from posts import views

urlpatterns = [
    path('create/post/', views.create_post, name='create_post'),
    path('view/post/<int:post_id>', views.view_post, name='view_post'),
]