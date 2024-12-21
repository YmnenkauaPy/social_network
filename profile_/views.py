from django.shortcuts import render, redirect, get_object_or_404
from profile_ import forms
from authentication.models import CustomUser
from posts.models import Post
from chats.models import Chat
from notifications.models import Notification

from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os, json

def get_last_seen_text(user):
    if user.is_online:
        return "online"
    
    if not user.last_activity:
        return "Last seen: unknown" 

    time_diff = now() - user.last_activity

    if time_diff < timedelta(minutes=1):
        return "Last seen a few seconds ago"
    
    elif time_diff < timedelta(hours=1):
        minutes = time_diff.seconds // 60
        return f"Last seen {minutes} minute{'s' if minutes > 1 else ''} ago"
    
    elif time_diff < timedelta(days=1):
        hours = time_diff.seconds // 3600
        return f"Last seen {hours} hour{'s' if hours > 1 else ''} ago"
    
    elif time_diff < timedelta(days=7):
        days = time_diff.days
        return f"Last seen {days} day{'s' if days > 1 else ''} ago"
    
    elif time_diff < timedelta(days=365):
        weeks = time_diff.days // 7
        return f"Last seen {weeks} week{'s' if weeks > 1 else ''} ago"
    
    else:
        years = time_diff.days // 365
        return f"Last seen {years} year{'s' if years > 1 else ''} ago"
    
def view_profile(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    online = get_last_seen_text(user)
    posts = Post.objects.filter(creator=user.id)
    notification = Notification.objects.filter(receiver=user, sender=request.user, name='Friends').order_by('-created_at').first()

    is_friend = request.user.friends.filter(id=user.id).exists()

    if notification and not is_friend and notification.answer != True:
        status = 'Request has been sent'
    elif is_friend:
        status = 'Unfriend'
    else:
        status = 'Add Friend'

    return render(request, 'profile/profile_view.html', {'custom_user':user, 'status':status,
                                                         "posts":posts, 'online':online, 
                                                         'is_creator': {post.id: post.creator.id == request.user.id for post in posts}})

def send_to_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        post_id = data.get('post_id')

        try:
            chat = Chat.objects.get(id=chat_id)
            post = Post.objects.get(id=post_id)
            chat.messages.create(content=f"http://192.168.0.106:8000/view/post/{post_id}", sender=request.user)
            return JsonResponse({'success': True, 'message': 'Сообщение отправлено!'})
        except Chat.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Чат не найден'})
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пост не найден'})
    return JsonResponse({'success': False, 'error': 'Некорректный запрос'})

def get_chats(request):
    chats = Chat.objects.filter(people=request.user)
    chats_data = [{'id': chat.id, 'name': chat.get_user_chat_name(request.user)} for chat in chats]

    return JsonResponse({'status':'ok', 'chats':chats_data})

def update_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = forms.ProfileForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=user.id)
    else:
        form = forms.ProfileForm(instance=user)

    return render(request, 'profile/update_profile.html', {'form': form})

def delete_profile(request, user_id):
    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        if user.profile_picture:
            image_path = user.profile_picture.path
            if os.path.isfile(image_path):
                os.remove(image_path)

        user.delete() 
        return redirect('main') 

    return redirect('profile', user_id = request.user.id)

def be_friends(request, to_whom, from_whom):
    if request.method == "POST":
        to_whom = CustomUser.objects.get(id=to_whom)
        from_whom = CustomUser.objects.get(id=from_whom)

        if to_whom.friends.filter(id=from_whom.id).exists():
            # Удаляем из друзей
            to_whom.friends.remove(from_whom)
            from_whom.friends.remove(to_whom)

            Notification.objects.create(
                name='Friends',
                description=f"{from_whom.username} stopped your friendship!",
                receiver=to_whom,
                sender=from_whom
            )
            Notification.objects.create(
                name='Friends',
                description=f"You stopped your friendship with {to_whom.username}!",
                receiver=from_whom,
                sender=from_whom
            )

            status = 'unfriend'

            # Удаляем чат, если он существует
            chats_to_delete = Chat.objects.filter(
                people=from_whom
            ).filter(
                people=to_whom
            )

            # Удалить найденные чаты
            chats_to_delete.delete()
        else:
            # Отправляем запрос на дружбу
            Notification.objects.create(
                name='Friends',
                description=f"{from_whom.username} sent you a friend's request!",
                receiver=to_whom,
                sender=from_whom
            )
            Notification.objects.create(
                name='Friends',
                description=f"You sent a friend's request to {to_whom.username}!",
                receiver=from_whom,
                sender=from_whom,
                answer=False
            )
            status = 'sent'

        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            f"user_{from_whom.id}",  # Группа по id получателя
            {
                "type": "send_notification",  # тип события в consumers
                'unread_count':from_whom.unread_notifications_count(),
            }
        )
        async_to_sync(layer.group_send)(
            f"user_{to_whom.id}",  # Группа по id получателя
            {
                "type": "send_notification",  # тип события в consumers
                'unread_count':to_whom.unread_notifications_count(),
            }
        )
        return JsonResponse({'status': 'ok', 'friend_status': status})


def search_for_users(request):
    search = request.GET.get('search', '') 
    users = CustomUser.objects.filter(username__icontains=search).exclude(id=request.user.id) if search else []
    
    users_ = {}

    for user in users:
        is_friend = request.user.friends.filter(id=user.id).exists()
        notification = Notification.objects.filter(receiver=user, sender=request.user, name='Friends').order_by('-created_at').first()

        if notification and not is_friend and not notification.answer:
            users_[user] = 'Request has been sent'
        elif is_friend:
            users_[user] = 'Unfriend'
        else:
            users_[user] = 'Add Friend'
    
    return render(request, 'profile/search_results.html', {'users': users_, 'type': 'results of searching'})

def related_users(request, user_id, relation_type):
    user = CustomUser.objects.get(id=user_id)
    related_users = getattr(user, relation_type).all()

    users_ = {}

    for user in related_users:
        notification = Notification.objects.filter(receiver=user, sender=request.user, name='Friends', description__icontains='sent').order_by('-created_at').first()
        if notification and not request.user in user.friends.all():
            users_[user] = 'Request has been sent'
        elif request.user in user.friends.all():
            users_[user] = 'Unfriend'
        else:
            users_[user] = 'Friend'

    return render(request, 'profile/related_users.html', {'users': users_, 'type':relation_type})

def toggle_follow_user(request, user_id):
    if request.method == 'POST':
        current_user = request.user
        user_to_toggle = get_object_or_404(CustomUser, id=user_id)
        
        if user_to_toggle != current_user:
            if user_to_toggle in current_user.followings.all():
                current_user.followings.remove(user_to_toggle)  #Unfollow
                user_to_toggle.followers.remove(current_user)
                status = 'unfollowed'

                #For person I unfollow
                notification = Notification(name='Unfollowed', description=f'{current_user.username} unfollowed you', receiver=user_to_toggle)
                notification.save() 

                #For me who I unfollowed
                notification = Notification(name='Unfollowed', description=f'You unfollowed {user_to_toggle.username}', receiver=current_user)
                notification.save() 

            else:
                current_user.followings.add(user_to_toggle)  #Follow
                user_to_toggle.followers.add(current_user)
                status = 'followed'

                #For person I follow
                notification = Notification(name='Followed', description=f'{current_user.username} followed you', receiver=user_to_toggle)
                notification.save()  

                #For me who I followed
                notification = Notification(name='Followed', description=f'You followed {user_to_toggle.username}', receiver=current_user)
                notification.save() 
            current_user.save()

            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                f"user_{user_to_toggle.id}",  # Группа по id получателя
                {
                    "type": "send_notification",  # тип события в consumers
                    'unread_count':user_to_toggle.unread_notifications_count(),
                }
            )

            async_to_sync(layer.group_send)(
                f"user_{current_user.id}",  # Группа по id получателя
                {
                    "type": "send_notification",  # тип события в consumers
                    'unread_count':current_user.unread_notifications_count(),
                }
            )

            return JsonResponse({'status': 'ok', 'follow_status': status})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)