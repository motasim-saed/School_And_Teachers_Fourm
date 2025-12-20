from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.forms import modelformset_factory
from user.forms import UserUpdateForm, CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import TeacherProfile, Qualification, Experience
from .forms import TeacherBasicProfileForm, TeacherProfileForm
from Schools.models import JobPosting, JobApplication, Notification # استيراد نماذج المدارس للتفاعل معها
from .forms import QualificationForm, ExperienceForm
from Schools.models import SchoolProfile
from django.db.models import Q,Count # للبحث المتقدم
# دالة مساعدة للتحقق من أن المستخدم هو "معلم"
def is_teacher(user):
    return user.is_authenticated and user.user_type == 'TEACHER'

# ===================================================================
# ١. لوحة التحكم الرئيسية للمعلم
# ===================================================================


@login_required
@user_passes_test(is_teacher)
def browse_schools_view(request):
    """
    يعرض قائمة بالمدارس المسجلة مع إحصائيات مفيدة.
    """
    # استخدام annotate لحساب عدد الوظائف وعدد المتقدمين لكل مدرسة
    schools = SchoolProfile.objects.annotate(
        # حساب عدد الوظائف النشطة لكل مدرسة
        active_jobs_count=Count('job_postings', filter=Q(job_postings__is_active=True)),
        
        # حساب إجمالي عدد طلبات التقديم على كل وظائف المدرسة
        total_applications_count=Count('job_postings__applications')
        
    ).order_by('-user__date_joined') # ترتيب المدارس من الأحدث للأقدم

    context = {
        'schools': schools,
    }
    return render(request, 'teachers/browse_schools.html', context)

@login_required
@user_passes_test(is_teacher)
def teacher_profile_view(request):
    profile = get_object_or_404(TeacherProfile, user=request.user)
    qualifications = profile.qualifications.all()
    experiences = profile.experiences.all()
    context = {
        'profile': profile,
        'qualifications': qualifications,
        'experiences': experiences,
    }
    return render(request, 'teachers/teacher_profile_view.html', context)




# دالة جديدة لعرض تفاصيل معلم (للمدارس أو العامة)
@login_required
def teacher_detail_view(request, pk):
    profile = get_object_or_404(TeacherProfile, pk=pk)
    qualifications = profile.qualifications.all()
    experiences = profile.experiences.all()
    context = {
        'profile': profile,
        'qualifications': qualifications,
        'experiences': experiences,
    }
    return render(request, 'teachers/teacher_detail.html', context)


# دالة جديدة لعرض تفاصيل مدرسة واحدة
@login_required
@user_passes_test(is_teacher)
def school_detail_view(request, pk):
    """
    يعرض صفحة التفاصيل الكاملة لمدرسة معينة.
    """
    school = get_object_or_404(SchoolProfile, pk=pk)
    # جلب الوظائف النشطة فقط لهذه المدرسة
    active_jobs = school.job_postings.filter(is_active=True)
    
    context = {
        'school': school,
        'active_jobs': active_jobs,
    }
    return render(request, 'teachers/school_detail.html', context)


@login_required
@user_passes_test(is_teacher)
def teacher_profile_edit_view(request):
    profile = get_object_or_404(TeacherProfile, user=request.user)
    user = request.user

    if request.method == 'POST':
        profile_form = TeacherBasicProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=user)
        password_form = CustomPasswordChangeForm(user, request.POST)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'تم تحديث بياناتك الشخصية بنجاح.')

            if request.POST.get('old_password'):
                if password_form.is_valid():
                    password_form.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
                else:
                    messages.error(request, 'فشل تغيير كلمة المرور. يرجى مراجعة الأخطاء.')
                    # أعد عرض الصفحة مع كل الفورمات لإظهار الأخطاء
                    context = {'profile_form': profile_form, 'user_form': user_form, 'password_form': password_form}
                    return render(request, 'teachers/teacher_profile_edit.html', context)
            
            return redirect('teachers:teacher_profile_view') # أعده لصفحة العرض

    else:
        profile_form = TeacherBasicProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=user)
        password_form = CustomPasswordChangeForm(user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'teachers/teacher_profile_edit.html', context)


@login_required
@user_passes_test(is_teacher, login_url='/login/') # توجيه غير المعلمين لصفحة الدخول
def teacher_dashboard_view(request):
    """
    تعرض لوحة التحكم الرئيسية للمعلم.
    هذه الصفحة هي نقطة الانطلاق للمعلم بعد تسجيل الدخول.
    """
    try:
        teacher_profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        # إذا لم يكن للمعلم ملف شخصي، نوجهه لإنشائه
        messages.info(request, 'مرحباً بك! يرجى إكمال ملفك الشخصي لبدء استخدام المنصة.')
        return redirect('teachers:profile_update')

    # إحصائيات سريعة للوحة التحكم
    applications_count = JobApplication.objects.filter(teacher=teacher_profile).count()
    accepted_count = JobApplication.objects.filter(teacher=teacher_profile, status='ACCEPTED').count()
    # profile = get_object_or_404(TeacherProfile, user=request.user)
    context = {

        'profile': teacher_profile,
        'applications_count': applications_count,
        'accepted_count': accepted_count,
    }
    return render(request, 'teachers/teacher_dashboard.html', context)

# ===================================================================
# ٢. إدارة الملف الشخصي (البيانات الأساسية، المؤهلات، الخبرات)
# ===================================================================


@login_required
@user_passes_test(is_teacher)
def profile_update_view(request):
    profile = get_object_or_404(TeacherProfile, user=request.user)

    # إعداد الفورم-ستس
    QualificationFormSet = modelformset_factory(
        Qualification, 
        fields=('degree', 'specialization', 'university', 'graduation_year'), 
        extra=1,  # اسمح بإضافة فورم واحد فارغ
        can_delete=True # اسمح بحذف المؤهلات الموجودة
    )
    ExperienceFormSet = modelformset_factory(
        Experience, 
        fields=('job_title', 'previous_school_name', 'start_date', 'end_date'), 
        extra=1, 
        form=ExperienceForm,
        can_delete=True
    )

    if request.method == 'POST':
        # نمرر بيانات POST إلى الفورم-ستس
        qual_formset = QualificationFormSet(request.POST, prefix='quals')
        exp_formset = ExperienceFormSet(request.POST, prefix='exps')

        if qual_formset.is_valid() and exp_formset.is_valid():
            
            # --- حفظ المؤهلات ---
            # أولاً، نحصل على الكائنات الجديدة دون حفظها في قاعدة البيانات
            new_quals = qual_formset.save(commit=False)
            for qual in new_quals:
                # نربط كل مؤهل جديد بالملف الشخصي للمعلم الحالي
                qual.teacher_profile = profile
                qual.save() # الآن نقوم بحفظه

            # --- حفظ الخبرات ---
            new_exps = exp_formset.save(commit=False)
            for exp in new_exps:
                # نربط كل خبرة جديدة بالملف الشخصي للمعلم الحالي
                exp.teacher_profile = profile
                exp.save()

            # --- التعامل مع الحذف ---
            # هذا الجزء يعالج الفورمات التي تم تحديد مربع "DELETE" فيها
            qual_formset.save()
            exp_formset.save()

            return redirect('teachers:teacher_profile_view') # توجيه لصفحة عرض الملف الشخصي

        else:
            # إذا فشل التحقق، اطبع الأخطاء في الكونسول لتراها
            print("Qualification Formset Errors:", qual_formset.errors)
            print("Experience Formset Errors:", exp_formset.errors)
            messages.error(request, 'حدث خطأ. يرجى مراجعة البيانات التي أدخلتها.')
            # ===============================================================

    else:
        # في حالة GET، نعرض الفورمات مع البيانات الحالية
        qual_formset = QualificationFormSet(queryset=Qualification.objects.filter(teacher_profile=profile), prefix='quals')
        exp_formset = ExperienceFormSet(queryset=Experience.objects.filter(teacher_profile=profile), prefix='exps')

    context = {
        'profile': profile,
        'qual_formset': qual_formset,
        'exp_formset': exp_formset,
    }
    return render(request, 'teachers/profile_form.html', context)

# ===================================================================
# ٣. عرض الوظائف والتقديم عليها
# ===================================================================
@login_required
@user_passes_test(is_teacher, login_url='/login/')
def job_list_view(request):
    """
    تعرض قائمة بجميع إعلانات الوظائف المتاحة.
    """
    jobs = JobPosting.objects.filter(is_active=True).order_by('-posted_at')
    context = {
        'jobs': jobs,
    }
    return render(request, 'teachers/job_list.html', context)

@login_required
@user_passes_test(is_teacher, login_url='/login/')
def job_detail_view(request, pk):
    """
    تعرض تفاصيل وظيفة معينة.
    """
    # السماح بعرض الوظيفة حتى لو كانت غير نشطة (is_active=False) إذا كان المعلم قد قدم عليها أو تم قبوله
    job = get_object_or_404(JobPosting, pk=pk)
    teacher_profile = request.user.teacher_profile
    
    # التحقق مما إذا كان المعلم قد قدم على هذه الوظيفة بالفعل
    has_applied = JobApplication.objects.filter(job=job, teacher=teacher_profile).exists()

    context = {
        'job': job,
        'has_applied': has_applied,
    }
    return render(request, 'teachers/job_detail.html', context)

@login_required
@user_passes_test(is_teacher, login_url='/login/')
def apply_for_job_view(request, pk):
    """
    تعالج طلب التقديم على وظيفة.
    """
    if request.method == 'POST':
        job = get_object_or_404(JobPosting, pk=pk, is_active=True)
        teacher_profile = request.user.teacher_profile

        # التحقق مرة أخرى قبل إنشاء الطلب
        if not JobApplication.objects.filter(job=job, teacher=teacher_profile).exists():
            # إنشاء طلب التوظيف
            JobApplication.objects.create(job=job, teacher=teacher_profile)

            # إنشاء إشعار للمدرسة صاحبة الإعلان
            message_for_school = f"لديك طلب توظيف جديد لوظيفة '{job.title}' من المعلم '{teacher_profile.full_name}'."
            Notification.objects.create(
                user=job.school.user,
                message=message_for_school,
                link=f"/schools/jobs/{job.pk}/applications/" # رابط لصفحة المتقدمين للوظيفة
            )
            
            messages.success(request, f"تم إرسال طلبك لوظيفة '{job.title}' بنجاح!")
        else:
            messages.warning(request, "لقد قدمت على هذه الوظيفة من قبل.")
        
        return redirect('teachers:job_detail', pk=pk)
    
    # إذا كان الطلب GET، يتم توجيهه لصفحة تفاصيل الوظيفة
    return redirect('teachers:job_detail', pk=pk)

# ===================================================================
# ٤. عرض طلباتي وحالتها
# ===================================================================
@login_required
@user_passes_test(is_teacher, login_url='/login/')
def my_applications_view(request):
    """
    تعرض قائمة بجميع الوظائف التي قدم عليها المعلم وحالة كل طلب.
    """
    teacher_profile = request.user.teacher_profile
    status_filter = request.GET.get('status')
    
    applications = JobApplication.objects.filter(teacher=teacher_profile)
    
    if status_filter:
        applications = applications.filter(status=status_filter)
        
    applications = applications.order_by('-applied_at')
    
    context = {
        'applications': applications,
        'current_status': status_filter,
    }
    return render(request, 'teachers/my_applications.html', context)



@login_required
@user_passes_test(is_teacher, login_url='/login/')
def profile_edit_basic_view(request):
    profile = get_object_or_404(TeacherProfile, user=request.user)
    
    if request.method == 'POST':
        form = TeacherBasicProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بياناتك الأساسية بنجاح.')
            return redirect('teachers:teacher_dashboard')
    else:
        form = TeacherBasicProfileForm(instance=profile)

    context = {
        'form': form
    }
    return render(request, 'teachers/profile_edit_basic.html', context)