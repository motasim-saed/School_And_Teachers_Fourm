from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from Schools.models import Notification
from core.onesignal import send_onesignal_notification

@receiver(post_save, sender=Message)
def notify_new_message(sender, instance, created, **kwargs):
    """
    إرسال إشعار عند استلام رسالة جديدة.
    """
    if created:
        # المرسل هو instance.sender
        # المستقبل هو الطرف الآخر في المحادثة
        conversation = instance.conversation
        recipients = conversation.participants.exclude(id=instance.sender.id)

        for recipient in recipients.all():
            # 1. إنشاء إشعار في قاعدة البيانات
            Notification.objects.create(
                user=recipient,
                message=f"رسالة جديدة من {instance.sender.username}: {instance.content[:30]}...",
                link=f"/messages/conversation/{conversation.id}/" # تم تصحيح الرابط ليطابق urls.py
            )

            # 2. إرسال إشعار OneSignal
            send_onesignal_notification(
                heading=f"رسالة جديدة من {instance.sender.username}",
                content=instance.content,
                user_ids=[recipient.id],
                data={"conversation_id": conversation.id}
            )
