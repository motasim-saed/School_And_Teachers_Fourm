from django.conf import settings

def onesignal_settings(request):
    return {
        'ONESIGNAL_APP_ID': getattr(settings, 'ONESIGNAL_APP_ID', None)
    }
