from .models import Chat

def unread_messages_processor(request):
    if request.user.is_authenticated:
        chats = Chat.objects.filter(people=request.user)
        total_unread = sum(chat.messages.unread_count(request.user) for chat in chats)
        return {"unread_msg": total_unread}
    return {}