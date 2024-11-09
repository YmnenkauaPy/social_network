from django.shortcuts import render, redirect
from authentication.models import CustomUser
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from profile_ import forms
import os

def view_profile(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    return render(request, 'profile/profile_view.html', {'custom_user':user})

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

    return render(request, 'profile/delete_profile.html')

def search_for_users(request):
    search = request.GET.get('search', '') 
    users = CustomUser.objects.filter(username__icontains=search) if search else []
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
                current_user.followings.remove(user_to_toggle)  # Отписываемся
                status = 'unfollowed'
            else:
                current_user.followings.add(user_to_toggle)  # Подписываемся
                status = 'followed'
            current_user.save()
            
            return JsonResponse({'status': 'ok', 'follow_status': status})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)