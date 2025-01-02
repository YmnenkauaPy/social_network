from authentication.models import CustomUser, Theme
from posts.models import Post
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login
from datetime import timedelta
from django.http import JsonResponse
from django.utils.timezone import now

def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("main")
        else:
            return render(request, "registration/login.html", {"error": "Invalid username or password"})

    return render(request, "registration/login.html")


def change_theme(request, theme):
    theme_ = get_object_or_404(Theme, id=1) #always only one
    theme_.color = theme
    theme_.save()
    return JsonResponse({'status':'ok'})

def get_current_theme(request):
    theme = Theme.objects.get(id=1)
    return JsonResponse({'theme': theme.color})

def main(request):
    if not request.user.is_authenticated:
        return redirect('login')

    time_frames = [
        (timedelta(days=3), '3 days'),
        (timedelta(weeks=1), 'week'),
        (timedelta(weeks=2), '2 weeks'),
        (timedelta(weeks=4), '1 month'),
        (timedelta(weeks=26), '6 months'),
        (timedelta(weeks=52), '1 year'),
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