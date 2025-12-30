
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import SchoolProfile, JobPosting, JobApplication, Notification
from .forms import SchoolProfileForm, JobPostingForm
from django.contrib import messages
from user.models import User
from django.db.models import Q, Count
from Teachers.models import TeacherProfile, Qualification, Experience
from django.db.models import Q # للبحث المتقدم


# استيراد الفورمات الجديدة
from user.forms import UserUpdateForm, CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash

 # دالة مساعدة للتحقق من نوع المستخدم (يجب تعريفها مرة واحدة فقط)
def is_school(user):
    return user.is_authenticated and user.user_type == User.UserType.SCHOOL

@login_required
def school_dashboard_view(request):
    """
    يعرض لوحة تحكم المدرسة بعد تسجيل الدخول بنجاح.
    """
    return render(request, 'schools/school_dashboard.html')
# # ----------------- دوال لوحة التحكم وإدارة الوظائف -----------------

@login_required
def job_application_management_view(request):
    """
    يعرض لوحة تحكم إدارة طلبات التوظيف مع خيارات البحث المتقدم عن المعلمين.
    """
    school_profile = get_object_or_404(SchoolProfile, user=request.user)
    job_postings = JobPosting.objects.filter(school=school_profile).annotate(application_count=Count('applications')).order_by('-posted_at')
    
    # منطق البحث المتقدم عن المعلمين
    teachers = TeacherProfile.objects.all()
    query = request.GET.get('q')
    specialization = request.GET.get('specialization')
    min_experience = request.GET.get('min_experience')

    if query:
        teachers = teachers.filter(
            Q(full_name__icontains=query) |
            Q(bio__icontains=query) |
            Q(qualifications__degree__icontains=query) |
            Q(qualifications__specialization__icontains=query) |
            Q(experiences__job_title__icontains=query)
        ).distinct()

    if specialization:
        teachers = teachers.filter(
            Q(qualifications__specialization__icontains=specialization) |
            Q(experiences__job_title__icontains=specialization)
        ).distinct()

    if min_experience:
        # هذا الجزء يتطلب منطقًا أكثر تعقيدًا لحساب سنوات الخبرة
        # ولكن يمكننا تبسيط الأمر للبحث عن معلمين لديهم خبرة على الأقل
        # مثال: نبحث عن الخبرات التي بدأت قبل عدد معين من السنوات
        pass

    context = {
        'job_postings': job_postings,
        'teachers': teachers,
        'query': query,
        'specialization': specialization,
        'min_experience': min_experience,
    }

    return render(request, 'schools/job_application_management.html', context)

# # ----------------- دوال إعلانات الوظائف والملف الشخصي -----------------
@login_required
@user_passes_test(is_school)
def school_profile_view(request):
    # استخدام get_object_or_404 آمن أكثر
    profile = get_object_or_404(SchoolProfile, user=request.user)
    context = {
        'profile': profile
    }
    return render(request, 'schools/school_profile_view.html', context)

# في Schools/views.py

# ... (بقية الاستيرادات)

@login_required
@user_passes_test(is_school)
def school_profile_edit_view(request):
    profile = get_object_or_404(SchoolProfile, user=request.user)
    user = request.user

    if request.method == 'POST':
        # إنشاء الفورمات الثلاثة مع بيانات POST
        profile_form = SchoolProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=user)
        password_form = CustomPasswordChangeForm(user, request.POST)

        # التحقق من صحة فورمات البيانات الشخصية
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'تم تحديث بيانات الملف الشخصي بنجاح.')
            
            # التحقق من فورم كلمة المرور (بشكل منفصل)
            # نتحقق إذا كان المستخدم قد أدخل شيئاً في حقل كلمة المرور القديمة
            # نتحقق من وجود كلمة المرور القديمة والجديدة معاً لتجنب التفعيل بالخطأ عبر الإكمال التلقائي
            if request.POST.get('old_password') and request.POST.get('new_password1'):
                if password_form.is_valid():
                    new_password_user = password_form.save()
                    # تحديث جلسة المستخدم للحفاظ على تسجيل دخوله
                    update_session_auth_hash(request, new_password_user)
                    messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
                else:
                    # إذا كان فورم كلمة المرور غير صالح، أضف أخطاءه للرسائل
                    for error in password_form.errors.values():
                        messages.error(request, error)
            
            return redirect('schools:school_profile_view')

    else:
        # إنشاء الفورمات الثلاثة بدون بيانات (للعرض)
        profile_form = SchoolProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=user)
        password_form = CustomPasswordChangeForm(user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'schools/school_profile_edit.html', context)




@login_required
def job_posting_list(request):
    school_profile = get_object_or_404(SchoolProfile, user=request.user)
    job_postings = JobPosting.objects.filter(school=school_profile).order_by('-posted_at')
    return render(request, 'schools/job_posting_list.html', {'job_postings': job_postings})

@login_required
def job_posting_create(request):
    school_profile = get_object_or_404(SchoolProfile, user=request.user)
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.school = school_profile
            job_posting.save()
            messages.success(request, 'تم إنشاء إعلان الوظيفة بنجاح.')
            return redirect('schools:job_posting_list')
    else:
        form = JobPostingForm()
    return render(request, 'schools/job_posting_form.html', {'form': form})

@login_required
def job_posting_update(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk, school__user=request.user)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث إعلان الوظيفة بنجاح.')
            return redirect('schools:job_posting_list')
    else:
        form = JobPostingForm(instance=job_posting)
    return render(request, 'schools/job_posting_form.html', {'form': form})

@login_required
def job_posting_delete(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk, school__user=request.user)
    if request.method == 'POST':
        job_posting.delete()
        messages.success(request, 'تم حذف إعلان الوظيفة بنجاح.')
        return redirect('schools:job_posting_list')
    return render(request, 'schools/job_posting_confirm_delete.html', {'job_posting': job_posting})

@login_required
def job_applications_list(request, job_pk):
    job_posting = get_object_or_404(JobPosting, pk=job_pk, school__user=request.user)
    applications = JobApplication.objects.filter(job=job_posting).select_related('teacher__user')
    return render(request, 'schools/job_applications_list.html', {'job_posting': job_posting, 'applications': applications})

# في Schools/views.py

@login_required
def update_application_status(request, application_pk):
    # تم تصحيح 'job_posting' إلى 'job'
    application = get_object_or_404(JobApplication, pk=application_pk, job__school__user=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        old_status = application.status

        if new_status in [choice[0] for choice in JobApplication.ApplicationStatus.choices]:
            if new_status != old_status:
                application.status = new_status
                application.save()

                # إنشاء إشعار للمعلم
                if new_status in ['ACCEPTED', 'REJECTED']:
                    if new_status == 'ACCEPTED':
                        message = f'تهانينا! تم قبول طلبك لوظيفة "{application.job.title}".'
                        
                        # إغلاق الوظيفة تلقائياً عند قبول معلم
                        job = application.job
                        job.is_active = False
                        job.save()
                        messages.info(request, f'تم إغلاق الوظيفة "{job.title}" تلقائياً بعد قبول المعلم.')
                        
                    else: # REJECTED
                        message = f'نأسف لإبلاغك، تم تحديث حالة طلبك لوظيفة "{application.job.title}" إلى مرفوض.'
                    
                    Notification.objects.create(
                        user=application.teacher.user,
                        message=message,
                        # يمكنك إضافة رابط لصفحة "طلباتي" الخاصة بالمعلم
                        link=f'/teachers/my-applications/' 
                    )

                messages.success(request, 'تم تحديث حالة الطلب بنجاح.')
            else:
                messages.info(request, 'لم يتم تغيير حالة الطلب.')
        else:
            messages.error(request, 'حالة غير صالحة.')
            
    # إعادة التوجيه إلى الصفحة التي جاء منها المستخدم، أو إلى صفحة افتراضية
    referer_url = request.META.get('HTTP_REFERER', 'schools:teachers_list')
    return redirect(referer_url)


# دالة إنشاء إشعار للمدرسة عند وجود طلب جديد
@login_required
def teacher_apply_to_job(request, job_pk):
    job_posting = get_object_or_404(JobPosting, pk=job_pk)
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # التحقق مما إذا كان المعلم قد قدم بالفعل على هذه الوظيفة
    if not JobApplication.objects.filter(job=job_posting, teacher=teacher_profile).exists():
        JobApplication.objects.create(job=job_posting, teacher=teacher_profile)
        
        # إنشاء إشعار للمدرسة التي نشرت الوظيفة
        school_user = job_posting.school.user
        message = f'لديك طلب وظيفة جديد على "{job_posting.title}" من المعلم {teacher_profile.full_name}.'
        application = JobApplication.objects.get(job=job_posting, teacher=teacher_profile)
        Notification.objects.create(
            user=school_user,
            message=message,
            link=f'/schools/applications/{application.pk}/detail/'
        )

        messages.success(request, 'تم إرسال طلبك بنجاح.')
    else:
        messages.warning(request, 'لقد قدمت على هذه الوظيفة من قبل.')
        
    return redirect('some_redirect_url')

# دالة عرض الإشعارات
@login_required
@user_passes_test(is_school)
def notification_list(request):
   
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # تحديث جميع الإشعارات غير المقروءة لتصبح مقروءة بمجرد فتح الصفحة
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'schools/notification_list.html', {'notifications': notifications})




# هذا هو الكود الصحيح
@login_required
@user_passes_test(is_school)
def teachers_list_view(request: HttpRequest):
    """
    تعرض قائمة بجميع المتقدمين على وظائف المدرسة.
    """
    # تم تصحيح 'job_posting' إلى 'job'
    applications = JobApplication.objects.filter(job__school__user=request.user).select_related(
        'teacher', 'teacher__user', 'job'
    ).order_by('-applied_at')

    context = {
        'applications': applications
    }
    return render(request, 'schools/teachers_list.html', context)


@login_required
@user_passes_test(is_school)
def browse_teachers_view(request):
    """
    تسمح للمدارس بتصفح قائمة المعلمين المسجلين والبحث فيهم.
    """
    # جلب كل المعلمين مع بيانات المستخدم المرتبطة بهم لتحسين الأداء
    teachers_list = TeacherProfile.objects.all().select_related('user').order_by('-user__date_joined')

    # --- منطق البحث والفلترة ---
    search_query = request.GET.get('q', '')
    specialization_query = request.GET.get('specialization', '')

    if search_query:
        teachers_list = teachers_list.filter(
            Q(full_name__icontains=search_query) |
            Q(bio__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    if specialization_query:
        # بحث في تخصصات المؤهلات أو الخبرات
        teachers_list = teachers_list.filter(
            Q(qualifications__specialization__icontains=specialization_query) |
            Q(experiences__job_title__icontains=specialization_query)
        ).distinct() # distinct() لمنع تكرار النتائج

    context = {
        'teachers': teachers_list,
        'search_query': search_query,
        'specialization_query': specialization_query,
    }
    return render(request, 'schools/browse_teachers.html', context)


@login_required
@user_passes_test(is_school)
def applicant_detail_view(request, application_pk):
    """
    يعرض التفاصيل الكاملة للمعلم المتقدم لوظيفة معينة.
    """
    application = get_object_or_404(JobApplication, pk=application_pk, job__school__user=request.user)
    teacher = application.teacher
    qualifications = teacher.qualifications.all()
    experiences = teacher.experiences.all()

    context = {
        'application': application,
        'teacher': teacher,
        'qualifications': qualifications,
        'experiences': experiences,
    }
    return render(request, 'schools/applicant_detail.html', context)