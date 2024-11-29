from django.shortcuts import render
from authentication.models import CustomUser
import notifications.models as m

def view_notifications(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    notifications = m.Notification.objects.filter(receiver__id=user_id).order_by('created_at')
    for i in notifications:
        i.read = True
        i.save()
    return render(request, 'features/view_notifications.html', {'custom_user':user, 'notifications':notifications})

