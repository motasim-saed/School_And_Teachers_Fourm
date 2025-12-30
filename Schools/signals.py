from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SchoolProfile, JobPosting, JobApplication, Notification
from core.onesignal import send_onesignal_notification
from user.models import User

@receiver(post_save, sender=SchoolProfile)
def notify_new_school(sender, instance, created, **kwargs):
    """
    إرسال إشعار عند تسجيل مدرسة جديدة.
    """
    if created:
        send_onesignal_notification(
            heading="مدرسة جديدة انضمت إلينا!",
            content=f"تمت إضافة مدرسة: {instance.school_name}",
            filters=[{"field": "tag", "key": "user_type", "relation": "=", "value": "TEACHER"}]
        )

@receiver(post_save, sender=JobPosting)
def notify_new_job(sender, instance, created, **kwargs):
    """
    إرسال إشعار عند نشر إعلان وظيفة جديد.
    """
    if created:
        send_onesignal_notification(
            heading="وظيفة شاغرة جديدة!",
            content=f"مدرسة {instance.school.school_name} تعلن عن وظيفة: {instance.title}",
            filters=[{"field": "tag", "key": "user_type", "relation": "=", "value": "TEACHER"}]
        )

@receiver(post_save, sender=JobApplication)
def notify_job_application_status(sender, instance, created, **kwargs):
    """
    1. إرسال إشعار للمدرسة عند التقديم الجديد.
    2. إرسال إشعار للمعلم عند قبول طلبه.
    """
    if created:
        # إشعار للمدرسة (صاحبة الوظيفة)
        school_user_id = instance.job.school.user.id
        send_onesignal_notification(
            content=f"المعلم {instance.teacher.full_name} تقدم لوظيفة: {instance.job.title}",
            user_ids=[school_user_id]
        )
        
        # إنشاء إشعار في قاعدة البيانات للمدرسة
        Notification.objects.create(
            user=instance.job.school.user,
            message=f"المعلم {instance.teacher.full_name} تقدم لوظيفة: {instance.job.title}",
            link=f"/schools/jobs/{instance.job.id}/applications/" # الرابط الصحيح لصفحة المتقدمين لهذه الوظيفة
        )
    else:
        # إذا تم تحديث الطلب (مثلاً حالة القبول)
        # نتحقق إذا تغيرت الحالة إلى ACCEPTED
        if instance.status == 'ACCEPTED':
            teacher_user_id = instance.teacher.user.id
            send_onesignal_notification(
                content=f"تم قبول انضمامك لمدرسة {instance.job.school.school_name} لوظيفة {instance.job.title}",
                user_ids=[teacher_user_id]
            )

            # إنشاء إشعار في قاعدة البيانات للمعلم
            Notification.objects.create(
                user=instance.teacher.user,
                message=f"تم قبول انضمامك لمدرسة {instance.job.school.school_name} لوظيفة {instance.job.title}",
                link="/teachers/my-applications/" # رابط طلباتي
            )
