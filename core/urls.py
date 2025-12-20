from django.urls import path
from . import views
app_name='core'
urlpatterns = [
    # الصفحة الرئيسية
    path('', views.HomePageView.as_view(), name='home'),
    
    # مسار بديل للصفحة الرئيسية (Function-based view)
    # path('', views.home_page_view, name='home'),
    
    # API للحصول على الإحصائيات
    # path('api/stats/', views.get_stats_ajax, name='get_stats_ajax'),
    
    # صفحات إضافية
    # path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    # path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    # path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    # path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),

    
]


