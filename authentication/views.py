from authentication import forms
from authentication.models import CustomUser
from django.shortcuts import redirect, render
from django.contrib.auth import login

def count_unread_notifications(request):
    user = CustomUser.objects.get(id=request.user.id)
    unread = user.unread_notifications_count()
    return unread

def main(request):
    unread = 0
    if request.user.is_authenticated: 
        unread = count_unread_notifications(request)
    return render(request, 'base.html', {'unread':unread})

def register(request):
    if request.method == 'POST':
        custom_user_form = forms.CustomUserForm(request.POST, request.FILES)
        
        if custom_user_form.is_valid():
            custom_user = custom_user_form.save()
            custom_user.save() 

            login(request, custom_user)
            return redirect('main')
    else:
        custom_user_form = forms.CustomUserForm()

    return render(request, 'registration/register.html', {'custom_user_form': custom_user_form})