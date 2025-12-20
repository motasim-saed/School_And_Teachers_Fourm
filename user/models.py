# user/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import validate_name_format
class User(AbstractUser):# هنا وراثه من موديل AbstractUser 
    """
    موديل المستخدم المخصص الذي يوسع الموديل الافتراضي لـ Django.
    """
    class UserType(models.TextChoices):
        TEACHER = 'TEACHER', 'معلم'
        SCHOOL = 'SCHOOL', 'مدرسة'

    # سنستخدم الحقول الافتراضية من AbstractUser مثل:
    # username, email, password, first_name, last_name

    # هذا هو الحقل الإضافي والمهم الذي يحدد نوع المستخدم
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        verbose_name='نوع المستخدم'
    )

    # يمكنك إضافة حقول أخرى مشتركة هنا، مثل رقم الجوال
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='رقم الجوال'
    )

    def __str__(self):
        return self.username
