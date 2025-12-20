from django.urls import path
from . import views
app_name='teachers'
urlpatterns = [
    # لوحة التحكم
    path('dashboard/', views.teacher_dashboard_view, name='teacher_dashboard'),

    # الملف الشخصي
    path('profile/', views.teacher_profile_view, name='teacher_profile_view'),
    path('profile/edit/', views.teacher_profile_edit_view, name='teacher_profile_edit'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('profile/edit-basic/', views.profile_edit_basic_view, name='profile_edit_basic'),
    # تفاصيل المعلم (عام/للمدارس)
    path('teacher/<int:pk>/', views.teacher_detail_view, name='teacher_detail'),

    # الوظائف
    path('jobs/', views.job_list_view, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail_view, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_for_job_view, name='apply_for_job'),
    path('browse-schools/', views.browse_schools_view, name='browse_schools'), 
    path('schools/<int:pk>/', views.school_detail_view, name='school_detail'),
    # طلباتي
    path('my-applications/', views.my_applications_view, name='my_applications'),
]
