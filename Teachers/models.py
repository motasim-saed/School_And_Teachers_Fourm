# Teachers/models.py

from django.db import models
from user.models import User # استيراد موديل المستخدم
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
from user.validators import validate_image_extension, validate_cv_extension, validate_file_size
# الدالة الديناميكية لمسار الصورة الشخصية للمعلم
def teacher_profile_pic_path(instance, filename):
   
    return f'teachers/user_{instance.user.id}/profile_pic/{filename}'

def teacher_cv_path(instance, filename):
    # المسار سيكون: media/teachers/user_{id}/cv/{filename}
    return f'teachers/user_{instance.user.id}/cv/{filename}'






class TeacherProfile(models.Model):# لجدول الرئيسي الذي يحتوي على المعلومات الشخصية للمعلم
    # علاقة واحد-لواحد مع موديل المستخدم
    user = models.OneToOneField( # هذا الحقل يربط كل ملف تعريف معلم بحساب واحد فقط 
        User,
        on_delete=models.CASCADE,
        primary_key=True,# المفتاح الاساسي 
        related_name='teacher_profile',#يسهل الوصول لملف المعلم من كائن المستخدم
        verbose_name='حساب المعلم'
    )
    # يمكننا استخدام first_name و last_name من موديل User
    # لكن إضافة full_name هنا قد يكون أسهل
    full_name = models.CharField(max_length=60, verbose_name='الاسم الكامل')

    profile_picture = models.ImageField(upload_to=teacher_profile_pic_path, null=True, blank=True, verbose_name='الصورة الشخصية',validators=[validate_image_extension, validate_file_size])
    bio = models.TextField(blank=True, verbose_name='نبذة تعريفية')
    cv_file = models.FileField(upload_to=teacher_cv_path, null=True, blank=True, verbose_name='ملف السيرة الذاتية',validators=[validate_cv_extension, validate_file_size])

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'ملف معلم'
        verbose_name_plural = 'ملفات المعلمين'

@receiver(post_delete, sender=TeacherProfile)
def delete_teacher_files_on_profile_delete(sender, instance, **kwargs):
    """
    هذه الدالة يتم استدعاؤها تلقائياً بعد حذف كائن TeacherProfile.
    تقوم بحذف الصورة الشخصية وملف السيرة الذاتية المرتبطين به.
    """
    # التحقق من وجود الصورة الشخصية وحذفها
    if instance.profile_picture:
        if os.path.isfile(instance.profile_picture.path):
            os.remove(instance.profile_picture.path)
            print(f"تم حذف الصورة: {instance.profile_picture.path}")

    # التحقق من وجود ملف السيرة الذاتية وحذفه
    if instance.cv_file:
        if os.path.isfile(instance.cv_file.path):
            os.remove(instance.cv_file.path)
            print(f"تم حذف السيرة الذاتية: {instance.cv_file.path}")
class Qualification(models.Model):# جدول لتخزين الشهادات والمؤهلات العلمية للمعلم.
    teacher_profile = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='qualifications',
        verbose_name='ملف المعلم'
    )
    degree = models.CharField(max_length=100, verbose_name='الدرجة العلمية')
    specialization = models.CharField(max_length=100, verbose_name='التخصص')
    university = models.CharField(max_length=100, verbose_name='الجامعة')
    graduation_year = models.PositiveIntegerField(
        verbose_name='سنة التخرج',
        validators=[
            MinValueValidator(2000), # الحد الأدنى للسنة
            MaxValueValidator(timezone.now().year) # الحد الأقصى هو السنة الحالية
        ]
    )

    def __str__(self):
        return f"{self.degree} في {self.specialization}"

    class Meta:
        verbose_name = 'مؤهل علمي'
        verbose_name_plural = 'المؤهلات العلمية'

class Experience(models.Model):# جدول لتخزين الخبرات الوظيفية السابقة للمعلم.
    teacher_profile = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='experiences',
        verbose_name='ملف المعلم'
    )
    job_title = models.CharField(max_length=100, verbose_name='المسمى الوظيفي')
    previous_school_name = models.CharField(max_length=100, verbose_name='اسم المدرسة السابقة')
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(null=True, blank=True, verbose_name='تاريخ النهاية')

    def __str__(self):
        return self.job_title

    class Meta:
        verbose_name = 'خبرة عملية'
        verbose_name_plural = 'الخبرات العملية'


