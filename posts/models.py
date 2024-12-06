from django.db import models
from django.conf import settings

class Post(models.Model):
    name = models.CharField(max_length = 32)
    description = models.TextField(blank=True, null=True)
    content = models.FileField(upload_to = "posts_media/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'creator_of_post')
    created_at = models.DateTimeField(auto_now_add = True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_to_post')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='creator_of_comment')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='like_to_comment')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_liked_comment')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')