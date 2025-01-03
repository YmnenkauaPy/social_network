from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import View
from posts import forms
from posts import models
import json, os

def create_post(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        content = request.FILES.get('content')
        link = request.POST.get('link')
        description = request.POST.get('description')

        form = forms.PostForm(request.POST, request.FILES)

        if not name:
            form.add_error('name', "You must provide a name for the post.")
        if not (content or link or description):
            form.add_error(None, "You must provide at least one type of content (file or link or description).")
        
        if form.is_valid():
            post = form.save(commit=False)
            post.name = name  
            post.description = description  
            post.creator = request.user

            post.save()
            return redirect('post_detail', post.id)
        else:
            print(form.errors)

    else:
        form = forms.PostForm(user=request.user)

    return render(request, 'posts/create_post.html')

def edit_post(request, pk):
    post = get_object_or_404(models.Post, id=pk)

    if request.method == 'POST':
        form = forms.PostForm(request.POST, request.FILES, instance=post)
        
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id = pk)
        else:
            print(form.errors)
    else:
        form = forms.PostForm(instance=post)

    return render(request, 'posts/edit_post.html', {'post':post})

def delete_post(request, pk):
    post = get_object_or_404(models.Post, id=pk)

    if request.method == 'POST': 
        if post.content:
            file_path = post.content.path
            if os.path.isfile(file_path):
                os.remove(file_path) 
        post.delete()
        return redirect('profile', user_id = request.user.id)  

    return redirect('profile', user_id = request.user.id)

def share_post(request, pk):
    pass

class PostDetailView(View):
    def get(self, request, post_id):
        post = get_object_or_404(models.Post, id=post_id)
        comments = post.comment_to_post.all() 
        user_liked_comments = {
            comment.id: comment.like_to_comment.filter(user=request.user).exists()
            for comment in comments
        }
        user_liked_post = post.like_to_post.filter(user=request.user).exists()
        return render(request, 'posts/view_post.html', {'post': post, 'comments': comments, 
            'user_liked_post':user_liked_post, 'user_liked_comments': user_liked_comments})

    def post(self, request, post_id):
        post = get_object_or_404(models.Post, id=post_id)
        content = request.POST.get('content')

        if content:  
            comment = models.Comment.objects.create(content=content, post=post, creator=request.user)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Проверка, AJAX ли запрос
                return JsonResponse({
                    'message': 'Comment added successfully!',
                    'comment': {
                        'id': comment.id,
                        'content': comment.content,
                        'creator': comment.creator.username,
                        'creator_id': comment.creator.id,
                        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                })
            
        return redirect('post_detail', post_id=post.id) 

class PostLikeToggle(View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(models.Post, pk=self.kwargs.get('pk'))
        like_qs = models.LikeToPost.objects.filter(post=post, user=request.user)
        liked = False
        if like_qs.exists():
            like_qs.delete()
        else:
            models.LikeToPost.objects.create(post=post, user=request.user)
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'likes_count': post.like_to_post.count(),
        })
    
def edit_comment(request, comment_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()

            if not content:
                return JsonResponse({'success': False, 'error': 'Content cannot be empty'}, status=400)

            comment = get_object_or_404(models.Comment, id=comment_id)
            comment.content = content
            comment.save()

            return JsonResponse({'success': True, 'content': comment.content})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def delete_comment(request, comment_id):
    comment = get_object_or_404(models.Comment, id=comment_id)

    if request.method == 'POST':  
        comment.delete()
        return redirect('post_detail', post_id=comment.post.id)  

    return redirect('post_detail')

class CommentLikeToggle(View):
    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(models.Comment, pk=self.kwargs.get('pk'))
        like_qs = models.Like.objects.filter(comment=comment, user=request.user)
        liked = False
        if like_qs.exists():
            like_qs.delete()
        else:
            models.Like.objects.create(comment=comment, user=request.user)
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'likes_count': comment.like_to_comment.count(),
        })
