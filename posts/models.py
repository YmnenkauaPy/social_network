from django.db import models
from django.conf import settings

class Post(models.Model):
    content = models.FileField(upload_to = "posts_media/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'creator_of_post')
    created_at = models.DateTimeField(auto_now_add = True)
