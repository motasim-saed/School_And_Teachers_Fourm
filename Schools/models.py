
from django.db import models
from user.models import User
from Teachers.models import TeacherProfile
from user.validators import validate_image_extension, validate_file_size

# الدالة الديناميكية لمسار شعار المدرسة
def school_logo_path(instance, filename):
    # instance هو كائن SchoolProfile الذي يتم حفظه
    # المسار سيكون: media/schools/user_{id}/logo/{filename}
    return f'schools/user_{instance.user.id}/logo/{filename}'


class SchoolProfile(models.Model):
    class SchoolType(models.TextChoices):
        PRIVATE = 'PRIVATE', 'أهلية'
        GOVERNMENT = 'GOVERNMENT', 'حكومية'
        INTERNATIONAL = 'INTERNATIONAL', 'دولية'

    user = models.OneToOneField(# وظيفة هذ السطر هي يربط كل ملف تعريف مدرسه بحساب مستخدم فقط 
        User,
        on_delete=models.CASCADE,# اذا تم حذف حساب المستخدم سيتم حذف حساب المستخدم من قاعدة البيانات
        primary_key=True,# لجعل حقل user هو الاساسي 
        related_name='school_profile', # هذا يسمح لك بالوصول الى ملف المدرسه من خلال كائن المستخدم بسهوله 
        verbose_name='حساب المدرسة'
    )
    school_name = models.CharField(max_length=50, verbose_name='اسم المدرسة')
    logo = models.ImageField(upload_to=school_logo_path, null=True, blank=True, verbose_name='شعار المدرسة',validators=[validate_image_extension, validate_file_size])
    school_type = models.CharField(max_length=20, choices=SchoolType.choices, verbose_name='نوع المدرسة')
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name='الموقع (المدينة، الحي)')
    
    def __str__(self):
        return self.school_name

    class Meta: # هذه الخاصيه تجعل الاعلانات تعرض دائما مرتبه من الاحدث الى الاقدم بشكل افتراضي عن استدعائها من قاعدة البيانات 
        verbose_name = 'ملف مدرسة'
        verbose_name_plural = 'ملفات المدارس'

class JobPosting(models.Model): # اعلان عن وظيفه
    school = models.ForeignKey( # هذا الحقل يربط كل اعلان وظيفه بالمدرسه التي نشرته 
        SchoolProfile,
        on_delete=models.CASCADE,# اذا تم حذف ملف المدرسه سيتم حذف جميع اعلانات الوظائف المرتبطه به تلقائيا 
        related_name='job_postings',#يسمح بالوصول السهل لجميع إعلانات المدرسة 
        verbose_name='المدرسة'
    )
    title = models.CharField(max_length=255, verbose_name='عنوان الوظيفة')
    description = models.TextField(verbose_name='وصف الوظيفة')
    required_specialization = models.CharField(max_length=100, verbose_name='التخصص المطلوب')# مثلا لغه عربيه او فيزياء 
    posted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ النشر')
    experience_years_required = models.PositiveIntegerField(null=True, blank=True, verbose_name='سنوات الخبرة المطلوبة')

     
    # =================== أضف هذا السطر هنا ===================
    is_active = models.BooleanField(default=True, verbose_name='نشط (مرئي للمعلمين)')
    # ========================================================

    def __str__(self):
        return self.title

    class Meta: # هذه الخاصيه تجعل الاعلانات تعرض دائما مرتبه من الاحدث الى الاقدم بشكل افتراضي عن استدعائها من قاعدة البيانات 
        verbose_name = 'إعلان وظيفة'
        verbose_name_plural = 'إعلانات الوظائف'
        ordering = ['-posted_at']

class JobApplication(models.Model): # طـــــــلب تقديم وظيفه
    # هنا نعرف حالات التقديم 
    class ApplicationStatus(models.TextChoices):
        PENDING = 'PENDING', 'قيد المراجعة'
        REVIEWED = 'REVIEWED', 'تمت المراجعة'
        ACCEPTED = 'ACCEPTED', 'مقبول'
        REJECTED = 'REJECTED', 'مرفوض'

    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='الوظيفة'
    )
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='المعلم'
    )
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التقديم')
    status = models.CharField(
        max_length=10,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        verbose_name='حالة الطلب'
    )

    def __str__(self):
        return f"طلب من {self.teacher.full_name} على وظيفة {self.job.title}"

    class Meta:
        verbose_name = 'طلب تقديم'
        verbose_name_plural = 'طلبات التقديم'
        unique_together = ('job', 'teacher') # منع التقديم مرتين
# نموذج جديد للإشعارات
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='المستخدم')
    message = models.TextField(verbose_name='الرسالة')
    link = models.URLField(max_length=200, blank=True, null=True, verbose_name='الرابط')
    is_read = models.BooleanField(default=False, verbose_name='هل تمت القراءة؟')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']

    def __str__(self):
        return f'إشعار لـ {self.user.username}'