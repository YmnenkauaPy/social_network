def unread_notifications(request):
    if request.user.is_authenticated:
        unread = request.user.unread_notifications_count()
        return {'unread': unread}
    return {'unread': 0}
