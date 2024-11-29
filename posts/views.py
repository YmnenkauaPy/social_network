from django.shortcuts import redirect, render
from posts import forms
from posts import models

def create_post(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        content = request.FILES.get('content')
        link = request.POST.get('link')
        description = request.POST.get('description')

        form = forms.PostForm(request.POST, request.FILES)

        if not name:
            form.add_error('name', "You must provide a name for the post.")
        if not (content or link):
            form.add_error(None, "You must provide at least one type of content (file or link).")

        if form.is_valid():
            post = form.save(commit=False)
            post.name = name  
            post.description = description  
            post.creator = request.user

            post.save()
            return redirect('view_post', post.id)
        else:
            print(form.errors)

    else:
        form = forms.PostForm(user=request.user)

    return render(request, 'posts/create_post.html')

def view_post(request, post_id):
    post = models.Post.objects.get(id=post_id)

    return render(request, 'posts/view_post.html', {'post':post})