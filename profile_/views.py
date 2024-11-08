from django.shortcuts import render, redirect
from authentication.models import CustomUser
from profile_ import forms

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
        user.delete() 
        return redirect('main') 

    return render(request, 'profile/delete_profile.html')
