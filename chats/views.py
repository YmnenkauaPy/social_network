from django.shortcuts import render, get_object_or_404
from chats import models
from django.http import JsonResponse
from profile_.views import get_last_seen_text
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
import os
from urllib.parse import quote

def upload_image(request):
    if request.method == 'POST' and 'image' in request.FILES:
        uploaded_file = request.FILES['image']

        upload_dir = 'messages_files/'
        fs = FileSystemStorage(location=os.path.join('media', upload_dir))
        filename = fs.save(uploaded_file.name, uploaded_file)

        safe_filename = quote(filename)

        file_url = f'/media/{upload_dir}{safe_filename}'

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
        unread_msg = chat.messages.all().filter(read=False).exclude(sender=request.user).count()
        chat.last_message = chat.messages.all().order_by('-sent_at')[0]
        chat.save()
        chats_.append({'chat':chat, 'chat_name':chat.get_user_chat_name(request.user), 'unread_msg':0})

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

    messages_data = [
        {
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.username,
            'sender_profile_pic': msg.sender.profile_picture.url,
            'content': msg.content,
            'sent_at': msg.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            'replied_to_content': msg.replied_to.content if msg.replied_to else None,
            'replied_to_id': msg.replied_to.id if msg.replied_to else None,
            'liked': msg.liked.count(),
            'user_liked': request.user in msg.liked.all(),
            'read': msg.read,
            'file_content': str(msg.file_content) if msg.file_content else None,
        }
        for msg in messages
    ]

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

def mark_read (request, pk):
    message = get_object_or_404(models.Message, id=pk)

    if not message.read:
        message.read = True
        message.save()
    return JsonResponse({'status':'ok'})