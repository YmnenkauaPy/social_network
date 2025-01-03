from authentication.models import CustomUser, Theme
from posts.models import Post
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login
from datetime import timedelta
from django.http import JsonResponse
from django.utils.timezone import now

from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.conf import settings
from django.apps import apps
from django.contrib.auth.forms import SetPasswordForm


User = apps.get_model(settings.AUTH_USER_MODEL)

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')

def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = get_user_model().objects.get(email=email)
                token = default_token_generator.make_token(user)

                uid = urlsafe_base64_encode(force_bytes(user.id))
                reset_link = f"http://{request.get_host()}/reset/password/{uid}/{token}/"

                subject = "Password Reset"
                message = f"Here is your password reset link: {reset_link}"

                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

                return redirect('login')
            except get_user_model().DoesNotExist:
                form.add_error('email', 'User with this email does not exist.')
                return render(request, 'forgot_password.html', {'form': form})
    else:
        form = PasswordResetForm()

    return render(request, 'forgot_password.html', {'form': form})

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                login(request, user)
                messages.success(request, "Your password has been reset successfully.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'reset_password.html', {'form': form})
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect('password_reset')

def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60)
            else:
                request.session.set_expiry(0)

            return redirect("main")
        else:
            return render(request, "registration/login.html", {"error": "Invalid username or password"})

    return render(request, "registration/login.html")


def change_theme(request, theme):
    try:
        theme_ = get_object_or_404(Theme, user=request.user)
    except:
        theme_ = Theme(user=request.user)
    theme_.color = theme
    theme_.save()
    return JsonResponse({'status':'ok'})

def get_current_theme(request):
    theme = Theme.objects.get(id=1)
    return JsonResponse({'theme': theme.color})

def main(request):
    if not request.user.is_authenticated:
        return redirect('login')
    time = '3 days'
    time_frames = [
        (timedelta(days=3), '3 days'),
        (timedelta(weeks=1), 'week'),
        (timedelta(weeks=2), '2 weeks'),
        (timedelta(weeks=4), 'month'),
        (timedelta(weeks=26), '6 months'),
        (timedelta(weeks=52), 'year'),
    ]

    friends = request.user.friends.all()
    followings = request.user.followings.all()
    user_ids = list(friends.values_list('id', flat=True)) + list(followings.values_list('id', flat=True))

    for time_frame, time_label  in time_frames:
        start_time = now() - time_frame
        posts = Post.objects.filter(
            creator_id__in=user_ids,
            created_at__gte=start_time
        ).order_by('-created_at')

        if posts.exists():
            time = time_label
            break

    user_posts = {}
    for post in posts:
        if post.creator not in user_posts:
            user_posts[post.creator] = []
        user_posts[post.creator].append(post)

    return render(request, 'registration/main.html', {
        'user_posts': user_posts,
        'friends': friends,
        'time':time,
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        profile_picture = request.FILES.get('profile_picture')
        details = request.POST.get('details')

        if not username or not password or not email:
            return render(request, 'registration/register.html', {
                'error_message': 'Username, Password, and Email are required!',
            })

        custom_user = CustomUser.objects.create(
            username=username,
            email=email,
            profile_picture=profile_picture,
            details=details
        )
        custom_user.set_password(password)
        custom_user.save()

        login(request, custom_user)
        return redirect('main')

    return render(request, 'registration/register.html')