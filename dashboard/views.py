from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.utils import timezone
from datetime import timedelta
from Schools.models import SchoolProfile, JobPosting, JobApplication
from Teachers.models import TeacherProfile
from messaging.models import Message, Conversation
from user.models import User

@login_required
@admin_required
def dashboard_home(request):
    """
    الصفحة الرئيسية للوحة تحكم المدير مع إحصائيات مفصلة.
    """
    # الإحصائيات العامة
    schools_count = SchoolProfile.objects.count()
    teachers_count = TeacherProfile.objects.count()
    jobs_count = JobPosting.objects.count()
    applications_count = JobApplication.objects.count()
    messages_count = Message.objects.count()
    conversations_count = Conversation.objects.count()
    
    # المستخدمين الجدد (آخر 7 أيام)
    seven_days_ago = timezone.now() - timedelta(days=7)
    new_users_count = User.objects.filter(date_joined__gte=seven_days_ago).count()
    
    context = {
        'schools_count': schools_count,
        'teachers_count': teachers_count,
        'jobs_count': jobs_count,
        'applications_count': applications_count,
        'messages_count': messages_count,
        'conversations_count': conversations_count,
        'new_users_count': new_users_count,
    }
    return render(request, 'dashboard/dashboard_home.html', context)

@login_required
@admin_required
def view_schools_list(request):
    """
    تعرض قائمة بكل المدارس المسجلة.
    """
    schools = SchoolProfile.objects.all().select_related('user').order_by('-user__date_joined')
    context = {
        'schools': schools
    }
    return render(request, 'dashboard/schools_list.html', context)

@login_required
@admin_required
def view_teachers_list(request):
    """
    تعرض قائمة بكل المعلمين المسجلين.
    """
    teachers = TeacherProfile.objects.all().select_related('user').order_by('-user__date_joined')
    context = {
        'teachers': teachers
    }
    return render(request, 'dashboard/teachers_list.html', context)
