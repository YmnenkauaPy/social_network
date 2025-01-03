from django.shortcuts import render, get_object_or_404, redirect
from authentication.models import CustomUser
import notifications.models as m
from chats.models import Chat, ChatName
from django.http import JsonResponse

def view_notifications(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    notifications = m.Notification.objects.filter(receiver__id=user_id).order_by('-created_at')
    for i in notifications:
        i.read = True
        i.save()

    return render(request, 'features/view_notifications.html', {'custom_user':user, 'notifications':notifications})

def accept_friend_request(request, notification_id):
    if request.method == "POST":
        notification = get_object_or_404(m.Notification, id=notification_id)

        if notification.answer is None:
            sender = notification.sender
            receiver = notification.receiver

            sender.friends.add(receiver)
            receiver.friends.add(sender)

            notification.answer = True
            notification.save()

            chat = Chat()
            chat.save()
            chat.people.add(sender, receiver)

            chatname = ChatName(chat=chat, user=sender, name=receiver.username)
            chatname.save()

            chatname = ChatName(chat=chat, user=receiver, name=sender.username)
            chatname.save()

            notif = m.Notification(name='Friends', description=f"{receiver} accepted your friend's request!", receiver=sender, sender=receiver)
            notif.save()

            return JsonResponse({'status': 'ok', 'message': 'Friend request accepted'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Request already processed'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def reject_friend_request(request, notification_id):
    if request.method == "POST":
        notification = get_object_or_404(m.Notification, id=notification_id)

        if notification.answer is None:
            sender = notification.sender
            receiver = notification.receiver

            notification.answer = False
            notification.save()

            notif = m.Notification(name='Friends', description=f"{receiver} rejected your friend's request!", receiver=sender, sender=receiver)
            notif.save()

            notif = m.Notification(name='Friends', description=f"You rejected {sender}'s friend's request!", receiver=receiver, sender=sender)
            notif.save()

            return JsonResponse({'status': 'ok', 'message': 'Friend request rejected'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Request already processed'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def delete_notification(request, pk):
    notif = get_object_or_404(m.Notification, id=pk)

    if request.method == 'POST':
        notif.delete()
        return redirect('notifications', user_id = request.user.id)

    return redirect('notifications', user_id = request.user.id)

def clear_notifications(request):
    notifications = m.Notification.objects.filter(receiver=request.user.id)

    for i in notifications:
        i.delete()

    return redirect('notifications', user_id = request.user.id)