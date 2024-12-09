from django.shortcuts import render, redirect
from authentication.models import CustomUser
from posts.models import Post
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from profile_ import forms
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from datetime import timedelta
from notifications.models import Notification
import os

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
    
    
def is_user_online(user):
    sessions = Session.objects.filter(expire_date__gte=now())
    for session in sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id):
            user.is_online = True
            user.last_activity = now()
            user.save(update_fields=['last_activity'])
            return True
    user.is_online = False
    return False

def view_profile(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    is_user_online(user)
    online = get_last_seen_text(user)
    posts = Post.objects.filter(creator=user.id)
    return render(request, 'profile/profile_view.html', {'custom_user':user, 'online':online, "posts":posts})

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

def search_for_users(request):
    search = request.GET.get('search', '') 
    users = CustomUser.objects.filter(username__icontains=search).exclude(id=request.user.id) if search else []
 
    return render(request, 'profile/search_results.html', {'users': users, 'type':'results of searching'})

def related_users(request, user_id, relation_type):
    user = CustomUser.objects.get(id=user_id)
    related_users = getattr(user, relation_type).all()
    return render(request, 'profile/search_results.html', {'users': related_users, 'type':relation_type})

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
                notification = Notification(name='Unfollowed', description=f'{current_user.username} unfollowed you')
                notification.save() 
                notification.receiver.add(user_to_toggle)

                #For me who I unfollowed
                notification = Notification(name='Unfollowed', description=f'You unfollowed {user_to_toggle.username}')
                notification.save() 
                notification.receiver.add(current_user)

            else:
                current_user.followings.add(user_to_toggle)  #Follow
                user_to_toggle.followers.add(current_user)
                status = 'followed'

                #For person I follow
                notification = Notification(name='Followed', description=f'{current_user.username} followed you')
                notification.save()  
                notification.receiver.add(user_to_toggle)  

                #For me who I followed
                notification = Notification(name='Followed', description=f'You followed {user_to_toggle.username}')
                notification.save() 
                notification.receiver.add(current_user)
            current_user.save()

            return JsonResponse({'status': 'ok', 'follow_status': status})

    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)