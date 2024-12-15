from django.shortcuts import render
from chats import models

def view_chats(request):
    chats = models.Chat.objects.filter(people=request.user)
    chats_ = {}

    for i in chats:
        other_person = i.people.exclude(id=request.user.id).first()
        other_person_name = other_person.username if other_person else "Unknown"
        chats_[other_person_name] = i

    return render(request, 'chats/chats.html', {'chats':chats_})