# في user/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# هذا الكلاس يسمح لنا بتخصيص كيفية عرض المستخدمين في لوحة التحكم
class UserAdmin(BaseUserAdmin):
    # الحقول التي ستظهر في قائمة المستخدمين
    list_display = ('username', 'email', 'user_type', 'is_staff', 'date_joined')
    # حقول يمكن البحث من خلالها
    search_fields = ('username', 'email')
    # فلاتر تظهر في الشريط الجانبي
    list_filter = ('user_type', 'is_staff', 'is_active', 'groups')
    
    # هذا الجزء مهم لعرض حقول إضافية في صفحة تعديل المستخدم
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('User Type', {'fields': ('user_type',)}), # عرض نوع المستخدم
    )

# تسجيل النموذج مع الكلاس المخصص
admin.site.register(User, UserAdmin)
