from django.shortcuts import render, get_object_or_404
from chats import models
from django.http import JsonResponse
from profile_.views import get_last_seen_text
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from asgiref.sync import async_to_sync
from urllib.parse import quote
from django.templatetags.static import static

def get_unread_counts(request):
    if request.user.is_authenticated:
        chats = models.Chat.objects.filter(people=request.user)
        unread_counts = [
            {"chat_id": chat.id, "unread_count": chat.unread_count(request.user)}
            for chat in chats
        ]
        return JsonResponse(unread_counts, safe=False)
    return JsonResponse([], safe=False)

def upload_image(request):
    if request.method == 'POST' and 'image' in request.FILES:
        uploaded_file = request.FILES['image']

        upload_dir = 'messages_files/'
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(os.path.join(upload_dir, uploaded_file.name), uploaded_file)

        safe_filename = quote(filename)
        file_url = f'{settings.MEDIA_URL}{safe_filename}'

        return JsonResponse({'imageUrl': file_url})

    return JsonResponse({'error': 'No image uploaded'}, status=400)

def delete_image(request, folder, filename):
    file_path = os.path.join('media', 'messages_files', filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return JsonResponse({'status': 'File deleted'})
    else:
        return JsonResponse({'error': 'File not found'}, status=404)

def view_chats(request):
    chats = models.Chat.objects.filter(people=request.user)
    chats_ = []

    for chat in chats:
        try:
            chat.last_message = chat.messages.all().order_by('-sent_at')[0]
        except:
            chat.last_message = None
        chat.save()
        unread = async_to_sync(chat.unread_count)(request.user)
        chats_.append({'chat':chat, 'chat_name':chat.get_user_chat_name(request.user), 'unread': unread})

    return render(request, 'chats/chats.html', {'chats':chats_})

def get_chat(request, pk):
    chat = get_object_or_404(models.Chat, id=pk)
    person = chat.get_another_person(request.user)
    last_seen = get_last_seen_text(person)

    return render(request, 'chats/chat.html', {'chat_id':pk, 'chat_name': chat.get_user_chat_name(request.user), 'last_seen':last_seen})

def get_messages(request, chat_id):
    chat = get_object_or_404(models.Chat, id=chat_id)

    messages = chat.messages.all().order_by('-sent_at')[:50]
    messages = messages[::-1]

    for msg in messages:
        if msg.sender != request.user:
            msg.read = True
            msg.save()

    messages_data = []

    for msg in messages:
        if msg.file_content:
            file_path = str(msg.file_content)
            clean_path = file_path.lstrip('/')
            if not os.path.exists(clean_path):
                msg.delete()
                continue

        messages_data.append({
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.username,
            'sender_profile_pic': msg.sender.profile_picture.url if msg.sender.profile_picture else static('images/None.png'),
            'content': msg.content,
            'sent_at': msg.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            'replied_to_content': msg.replied_to.content if msg.replied_to else None,
            'replied_to_id': msg.replied_to.id if msg.replied_to else None,
            'liked': msg.liked.count(),
            'user_liked': request.user in msg.liked.all(),
            'read': msg.read,
            'file_content': str(msg.file_content) if msg.file_content else None,
        })

    return JsonResponse({'messages': messages_data})

def liked_message(request, pk):
    message = get_object_or_404(models.Message, id=pk)

    if request.user not in message.liked.all():
        message.liked.add(request.user)
        message.save()
        return JsonResponse({'status':'ok', 'liked':int(message.liked.count()), 'user_liked':True})
    else:
        message.liked.remove(request.user)
        message.save()
        return JsonResponse({'status':'ok', 'liked':int(message.liked.count()), 'user_liked':False})

def mark_read(request, pk):
    message = get_object_or_404(models.Message, id=pk)

    if not message.read:
        message.read = True
        message.save()
    return JsonResponse({'status':'ok'})