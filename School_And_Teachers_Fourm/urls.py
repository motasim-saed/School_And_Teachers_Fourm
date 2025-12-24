import os
from django.conf import settings
from django.http import HttpResponse
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib import admin
from django.urls import path,include

def onesignal_js(request, filename):
    # هذا الكود يقرأ الملف ويرسله للمتصفح مع النوع الصحيح
    file_path = os.path.join(settings.BASE_DIR, 'static', filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/javascript")
            # إضافة هذا الرأس لحل مشكلة متصفحات Chrome و Edge
            response['Service-Worker-Allowed'] = '/'
            return response
    return HttpResponse(status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('teachers/',include('Teachers.urls',namespace='teachers')),
    path('schools/',include('Schools.urls',namespace='schools')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),      path('user/',include('user.urls',namespace='user')),
    path('',include('core.urls',namespace='core')),
    path('messages/', include('messaging.urls', namespace='messaging')),
    path('OneSignalSDKWorker.js', onesignal_js, {'filename': 'OneSignalSDKWorker.js'}),
    path('OneSignalSDKUpdaterWorker.js', onesignal_js, {'filename': 'OneSignalSDKUpdaterWorker.js'}),
    # path('',include('visitor.urls',namespace='visitor')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
