from django.conf import settings


def google_oauth(request):
    return {'google_oauth_configured': settings.GOOGLE_OAUTH_CONFIGURED}


def unread_notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    else:
        count = 0
    return {'unread_notifications_count': count}
