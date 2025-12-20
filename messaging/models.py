from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """
    Represents a conversation between two or more users.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='conversations',
        verbose_name='المشاركون'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ آخر تحديث')

    class Meta:
        verbose_name = 'محادثة'
        verbose_name_plural = 'محادثات'
        ordering = ['-updated_at']

    def __str__(self):
        return f"محادثة بين {', '.join([user.username for user in self.participants.all()])}"

class Message(models.Model):
    """
    Represents a single message within a conversation.
    """
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        verbose_name='المحادثة'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name='المرسل'
    )
    content = models.TextField(verbose_name='محتوى الرسالة')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='חותמת זמן')
    is_read = models.BooleanField(default=False, verbose_name='مقروءة')

    class Meta:
        verbose_name = 'رسالة'
        verbose_name_plural = 'رسائل'
        ordering = ['timestamp']

    def __str__(self):
        return f"رسالة من {self.sender.username} في {self.timestamp.strftime('%Y-%m-%d %H:%M')}"