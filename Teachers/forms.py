# Teachers/forms.py

from django import forms
from .models import TeacherProfile,Qualification,Experience

class TeacherProfileForm(forms.ModelForm):
    """
    فورم للبيانات الإضافية الخاصة بالمعلم.
    """
    class Meta:
        model = TeacherProfile
        # نأخذ الحقول من موديل TeacherProfile
        fields = [ 'profile_picture', 'bio', 'cv_file']
        # نستبعد حقل 'user' لأنه سيتم ربطه برمجياً

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['full_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'الاسم الكامل كما سيظهر في ملفك الشخصي'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
        self.fields['bio'].widget.attrs.update({'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب نبذة مختصرة عنك...'})
        self.fields['cv_file'].widget.attrs.update({'class': 'form-control'})


# ===================================================================
class TeacherBasicProfileForm(forms.ModelForm):
    """
    فورم لتعديل البيانات الأساسية للمعلم (الصورة، النبذة، السيرة الذاتية).
    """
    class Meta:
        model = TeacherProfile
        fields = ['profile_picture', 'bio', 'cv_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].required = False
        self.fields['bio'].widget.attrs.update({'class': 'form-control', 'rows': 4})
        self.fields['cv_file'].widget.attrs.update({'class': 'form-control'})
        self.fields['cv_file'].required = False

class QualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = ['degree', 'specialization', 'university', 'graduation_year']
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'university': forms.TextInput(attrs={'class': 'form-control'}),
            # =================== هذا هو التعديل الرئيسي هنا ===================
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 2020'}),
            # ===============================================================
        }
#تنسيق الادخال في الفورم للتاريخ 
class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'previous_school_name', 'start_date', 'end_date']
        # =================== هذا هو التعديل الرئيسي هنا ===================
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }