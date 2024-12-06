from django.urls import path
from posts import views

urlpatterns = [
    path('create/post/', views.create_post, name='create_post'),
    path('view/post/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('comment/like/<int:pk>/', views.CommentLikeToggle.as_view(), name='comment_like_toggle'),
    path('edit/comment/<int:comment_id>/', views.edit_comment, name='comment_edit'),
    path('delete/comment/<int:comment_id>', views.delete_comment, name='comment_delete'),
]
