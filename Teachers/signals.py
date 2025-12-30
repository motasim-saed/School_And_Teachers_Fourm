from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TeacherProfile
from core.onesignal import send_onesignal_notification

@receiver(post_save, sender=TeacherProfile)
def notify_new_teacher(sender, instance, created, **kwargs):
    """
    إرسال إشعار عند تسجيل معلم جديد.
    """
    if created:
        send_onesignal_notification(
            heading="معلم جديد انضم إلينا!",
            content=f"انضم المعلم: {instance.full_name} إلى المنصة.",
            filters=[{"field": "tag", "key": "user_type", "relation": "=", "value": "SCHOOL"}]
        )
