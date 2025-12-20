# # schools/forms.py

from django import forms
from .models import SchoolProfile, JobPosting
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = ['school_name', 'logo', 'school_type', 'location']
        widgets = {
            'school_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المدرسة'
            }),
            'school_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الموقع (المدينة، الحي)'
            }),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['logo'].required = False

class SchoolRegistrationProfileForm(SchoolProfileForm):
    """
    فورم مخصص لعملية التسجيل، حيث يتم استبعاد اسم المدرسة
    لأنه يتم إدخاله بالفعل في الفورم الأساسي (UserForm).
    """
    class Meta(SchoolProfileForm.Meta):
        exclude = ['school_name']



class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'required_specialization', 'experience_years_required']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان الوظيفة'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'وصف الوظيفة'
            }),
            'required_specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'التخصص المطلوب (مثال: لغة عربية، فيزياء)'
            }),
            'experience_years_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد سنوات الخبرة المطلوبة (أرقام فقط)'
            }),
        }


@receiver(post_delete, sender=SchoolProfile)
def delete_school_logo_on_profile_delete(sender, instance, **kwargs):
    """
    هذه الدالة يتم استدعاؤها تلقائياً بعد حذف كائن SchoolProfile.
    تقوم بحذف شعار المدرسة المرتبط به.
    """
    # التحقق من وجود الشعار وحذفه
    if instance.logo:
        if os.path.isfile(instance.logo.path):
            os.remove(instance.logo.path)
            print(f"تم حذف الشعار: {instance.logo.path}")