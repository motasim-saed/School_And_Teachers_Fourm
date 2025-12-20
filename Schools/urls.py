# schools/urls.py
from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    # لوحة التحكم والملف الشخصي
    path('dashboard/', views.school_dashboard_view, name='school_dashboard'),


    # إدارة إعلانات الوظائف
    path('jobs/', views.job_posting_list, name='job_posting_list'),
    path('jobs/create/', views.job_posting_create, name='job_posting_create'),
    path('jobs/<int:pk>/update/', views.job_posting_update, name='job_posting_update'),
    path('jobs/<int:pk>/delete/', views.job_posting_delete, name='job_posting_delete'),

    # إدارة طلبات التوظيف
    path('applications/management/', views.job_application_management_view, name='job_application_management'),
    path('jobs/<int:job_pk>/applications/', views.job_applications_list, name='job_applications_list'),
    path('applications/<int:application_pk>/detail/', views.applicant_detail_view, name='applicant_detail'),
    
    # تم الاحتفاظ بهذا المسار المنطقي لتحديث حالة الطلب
    path('applications/<int:application_pk>/update-status/', views.update_application_status, name='update_application_status'),

    path('browse-teachers/', views.browse_teachers_view, name='browse_teachers'),    path('teachers/list/', views.teachers_list_view, name='teachers_list'),

    # الإشعارات
    path('notifications/', views.notification_list, name='notification_list'),
      # =================== المسارات الجديدة للملف الشخصي ===================
    path('profile/', views.school_profile_view, name='school_profile_view'),
    path('profile/edit/', views.school_profile_edit_view, name='school_profile_edit'),
    # ========
    # تم حذف المسار المكرر من هنا
]
