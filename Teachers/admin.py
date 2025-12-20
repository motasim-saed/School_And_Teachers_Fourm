# في Teachers/admin.py

from django.contrib import admin
from .models import TeacherProfile, Qualification, Experience

# هذا الكلاس يسمح بإضافة المؤهلات والخبرات مباشرة من صفحة المعلم
class QualificationInline(admin.TabularInline):
    model = Qualification
    extra = 1 # عدد الفورمات الفارغة التي ستظهر

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'get_email') # سنضيف دالة لجلب الإيميل
    search_fields = ('full_name', 'user__username')
    inlines = [QualificationInline, ExperienceInline] # هنا السحر!

    @admin.display(description='البريد الإلكتروني')
    def get_email(self, obj):
        return obj.user.email

# ليس من الضروري تسجيل المؤهلات والخبرات بشكل منفصل
# لأننا نديرها من خلال المعلم، ولكن تسجيلها يسمح بالوصول المباشر إليها
@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ('teacher_profile', 'degree', 'specialization', 'university')
    search_fields = ('teacher_profile__full_name', 'degree', 'specialization')

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('teacher_profile', 'job_title', 'previous_school_name')
    search_fields = ('teacher_profile__full_name', 'job_title')
