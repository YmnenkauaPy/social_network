from django.shortcuts import render, get_object_or_404
from chats import models
from django.http import JsonResponse
# from profile_.views import get_last_seen_text, is_user_online

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
    # is_user_online(person)
    # last_seen = get_last_seen_text(person)
    last_seen = '12 PM'
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
        }
        for msg in messages
    ]

    return JsonResponse({'messages': messages_data})
