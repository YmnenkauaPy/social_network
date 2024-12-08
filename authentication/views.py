from authentication import forms
from authentication.models import CustomUser
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login

def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Проверяем пользователя
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("main")  # Редирект на главную или другую страницу
        else:
            # Если данные некорректны
            return render(request, "registration/login.html", {"error": "Invalid username or password"})

    return render(request, "registration/login.html")


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
        username = request.POST.get('username')
        password = request.POST.get('password')
        profile_picture = request.FILES.get('profile_picture')  

        if not username or not password:
            return render(request, 'registration/register.html', {
                'error_message': 'Username and Password are required!',
            })

        custom_user = CustomUser.objects.create(
            username=username,
            profile_picture=profile_picture
        )
        custom_user.set_password(password)  
        custom_user.save()

        login(request, custom_user)
        return redirect('main')

    return render(request, 'registration/register.html')