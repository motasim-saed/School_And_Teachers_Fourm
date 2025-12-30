from django.conf import settings
from Schools.models import Notification

def onesignal_settings(request):
    return {
        'ONESIGNAL_APP_ID': getattr(settings, 'ONESIGNAL_APP_ID', None)
    }

def unread_notifications(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
