from django.db import models
from django.contrib.auth.models import AbstractUser
from posts.models import Post
from django.apps import apps

class CustomUser(AbstractUser):
    details = models.CharField(max_length=100, default='')
    profile_picture = models.ImageField(upload_to='profile_media/', blank=True, null=True)
    posts = models.ManyToManyField(Post, related_name='posts_of_user', blank=True)
    friends = models.ManyToManyField('self', symmetrical=False, related_name='friends_of_user', blank=True)
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followings_of_user', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='followers_of_user', blank=True)
    is_online = models.BooleanField(default=False)
    email = models.EmailField()
    last_activity = models.DateTimeField(null=True, blank=True)

    def unread_notifications_count(self):
        Notification = apps.get_model('notifications', 'Notification')
        return Notification.objects.filter(
            receiver=self,
            read=False
        ).count()

class Theme(models.Model):
    color = models.CharField(max_length=5, default='light')