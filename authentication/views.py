from authentication import forms
from authentication.models import CustomUser
from posts.models import Post
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from datetime import timedelta
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


def count_unread_notifications(user):
    user = CustomUser.objects.get(id=user.id)
    unread = user.unread_notifications_count()
    return unread

def main(request):
    if not request.user.is_authenticated:
        return redirect('login')
    three_days_ago = now() - timedelta(days=3)
    friends = request.user.friends.all()
    followings = request.user.followings.all()
    user_ids = list(friends.values_list('id', flat=True)) + list(followings.values_list('id', flat=True))
    
    posts = Post.objects.filter(
        creator_id__in=user_ids,
        created_at__range=[three_days_ago, now()]
    ).order_by('-created_at')

    user_posts = {}
    for post in posts:
        if post.creator not in user_posts:
            user_posts[post.creator] = []
        user_posts[post.creator].append(post)

    return render(request, 'registration/main.html', {
        'user_posts': user_posts,
        'friends': friends,
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