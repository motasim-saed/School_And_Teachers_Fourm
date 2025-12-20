from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
app_name='user'
urlpatterns = [
   
     # مسارات التسجيل الجديدة
    path('register/', views.register_choice_view, name='register_choice'),
    path('register/teacher/', views.register_teacher_view, name='register_teacher'),
    path('register/school/', views.register_school_view, name='register_school'),

     path('login/', views.login_view, name='login'),
     path('logout_view/', views.logout_view, name='logout_view'),
     path('password-reset/', 
          auth_views.PasswordResetView.as_view(template_name='user/password_reset_form.html',
             # =================== هذا هو السطر الجديد والمهم ===================
             email_template_name='registration/password_reset_email.html' 
             # ===============================================================
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'), 
         name='password_reset_done'),
         
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'), 
         name='password_reset_confirm'),
         
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'), 
         name='password_reset_complete'),
]

