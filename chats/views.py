from django.shortcuts import render, get_object_or_404
from chats import models
from django.http import JsonResponse
from profile_.views import get_last_seen_text

def view_chats(request):
    chats = models.Chat.objects.filter(people=request.user)
    chats_ = []
    for chat in chats:
        try:
            last_message = (chat.messages.order_by('-sent_at')[:1][0]).content
        except:
            last_message = 'There is no messages'
        chats_.append({'chat':chat, 'chat_name':chat.get_user_chat_name(request.user), 'last_message': last_message})
    
    return render(request, 'chats/chats.html', {'chats':chats_})

def get_chat(request, pk):
    chat = get_object_or_404(models.Chat, id=pk)
    person = chat.get_another_person(request.user)
    last_seen = get_last_seen_text(person)
    return render(request, 'chats/chat.html', {'chat_id':pk, 'chat_name': chat.get_user_chat_name(request.user), 'last_seen':last_seen})

def get_messages(request, chat_id):
    chat = get_object_or_404(models.Chat, id=chat_id)
    messages = chat.messages.order_by('sent_at')[:50]  # Последние 50 сообщений

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
            'liked': msg.liked,
        }
        for msg in messages
    ]

    return JsonResponse({'messages': messages_data})

def liked_message(request, pk):
    message = get_object_or_404(models.Message, id=pk)

    if not message.liked:
        message.liked = True
        message.save()
        return JsonResponse({'status':'ok', 'liked':'1'})
    else:
        message.liked = False
        message.save()
        return JsonResponse({'status':'ok', 'liked':'0'})
    
def mark_read (request, pk):
    message = get_object_or_404(models.Message, id=pk)

    if not message.read:
        message.read = True
        message.save()
    return JsonResponse({'status':'ok'})