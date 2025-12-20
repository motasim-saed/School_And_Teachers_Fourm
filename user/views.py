# views.py - واجهة الصفحة الرئيسية مع الإحصائيات الديناميكية

from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from .forms import UserBaseForm, SchoolBaseForm 
from django.contrib.auth import logout
from Teachers.forms import TeacherProfileForm
from Schools.forms import SchoolProfileForm, SchoolRegistrationProfileForm
from .models import User
from django.contrib.auth import login, authenticate
from .forms import UserLoginForm 
from Emails.views import send_welcome_email

# 1. دالة عرض صفحة الاختيار
def register_choice_view(request):
    return render(request, 'user/register_choice.html')

# 2. دالة عرض وتسجيل المعلم
@transaction.atomic
def register_teacher_view(request):
    if request.method == 'POST':
        user_form = UserBaseForm(request.POST)
        profile_form = TeacherProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():

            first_name=user_form.cleaned_data.get('first_name')
            last_name=user_form.cleaned_data.get('last_name')
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.user_type = User.UserType.TEACHER
            user.save()

            profile = profile_form.save(commit=False)
            profile.user=user
            profile.full_name= f"{first_name } { last_name}".strip()
            profile.save()
            send_welcome_email(username=user.first_name, recipient_email=user.email)
            login(request,user)

            messages.success(request, f"أهلاً بك {user.first_name}! تم إنشاء ملفك الشخصي.")
            messages.info(request, "الآن، يرجى إضافة مؤهلاتك وخبراتك لتكتمل فرصك في الحصول على وظيفة.")
            
            # 3. التوجيه لصفحة إضافة المؤهلات والخبرات
            return redirect('teachers:profile_update')
    else:
        user_form = UserBaseForm()
        profile_form = TeacherProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'user/register_teacher.html', context)

## في user/views.py

@transaction.atomic
def register_school_view(request):
    if request.method == 'POST':
        user_form = SchoolBaseForm(request.POST)
        profile_form = SchoolRegistrationProfileForm(request.POST, request.FILES) # استخدام الفورم الجديد

        if user_form.is_valid() and profile_form.is_valid():
            # ... (منطق الحفظ يبقى كما هو) ...
            school_name = user_form.cleaned_data.get('last_name')
            user = user_form.save(commit=False)
            user.first_name = "مدرســة"
            user.set_password(user_form.cleaned_data['password'])
            user.user_type = User.UserType.SCHOOL
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.school_name = school_name
            profile.save()
            send_welcome_email(username=school_name, recipient_email=user.email)
            login(request, user)
            messages.success(request, f"أهلاً بكِ، {school_name}! تم إنشاء حساب المدرسة بنجاح.")
            return redirect('schools:school_dashboard')
        
        # =================== هذا هو الجزء المضاف والمهم ===================
        else:
            # إذا كان أحد الفورمات غير صالح، أضف رسالة خطأ عامة
            messages.error(request, 'حدث خطأ. يرجى مراجعة الحقول التي تحتوي على أخطاء.')
        # ===============================================================

    else:
        user_form = SchoolBaseForm()
        profile_form = SchoolRegistrationProfileForm() # استخدام الفورم الجديد

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'user/register_school.html', context)

#__________تسجيل الدخول ________

# --- دالة تسجيل الدخول ---
def login_view(request):
   
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            messages.success(request, f"مرحباً بعودتك، {user.username}!")
            
            # --- التوجيه بناءً على نوع المستخدم ---
            if user.user_type == User.UserType.SCHOOL:
                return redirect('schools:school_dashboard')
            elif user.user_type == User.UserType.TEACHER:
              return redirect('teachers:teacher_dashboard')            # يمكنك إضافة مسار افتراضي في حال لم يتطابق أي شرط
            else:
                return redirect('teachers:teacher_dashboard')  # مسار صفحة رئيسية أو لوحة تحكم عامة
    else:
        form = UserLoginForm()
        
    return render(request, 'user/login.html', {'form': form})


def logout_view(request):
    """
    تقوم بتسجيل خروج المستخدم الحالي وإنهاء الجلسة (session).
    """
    # استدعاء دالة تسجيل الخروج الجاهزة من جانغو
    logout(request)
    
    # (اختياري ولكن موصى به) إضافة رسالة للمستخدم
    messages.success(request, "تم تسجيل خروجك بنجاح.")
    
    # إعادة توجيه المستخدم إلى الصفحة الرئيسية أو أي صفحة أخرى
    return redirect('user:register_choice') #