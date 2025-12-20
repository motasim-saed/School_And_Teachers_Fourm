# user/forms.py

from django import forms
from .models import User
# --- استيراد جديد ---
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm

class UserBaseForm(forms.ModelForm):
    """
    فورم للبيانات الأساسية للمستخدم (مشترك بين المعلم والمدرسة).
    """
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    confirm_password = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = User
        # نأخذ الحقول الأساسية من موديل User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تعريب التسميات (Labels)
        self.fields['first_name'].label = "الاسم الأول"
        self.fields['last_name'].label = "الاسم الأخير"
        self.fields['username'].label = "اسم المستخدم (باللغة الإنجليزية)"
        self.fields['email'].label = "البريد الإلكتروني"
        self.fields['phone_number'].label = "رقم الجوال"

        # حذف رسائل المساعدة الإنجليزية المزعجة
        self.fields['username'].help_text = '' 
        # إضافة تنسيقات Bootstrap
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'example@example.com'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("كلمتا المرور غير متطابقتين!")
        return confirm_password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("اسم المستخدم هذا محجوز، يرجى اختيار اسم آخر.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مسجل لدينا بالفعل.")
        return email


class SchoolBaseForm(UserBaseForm):
    """
    فورم يرث من الفورم الأساسي ويقوم بإخفاء حقول الاسم الأول والأخير.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إخفاء الحقول غير المرغوب فيها
        self.fields['first_name'].widget = forms.HiddenInput()
        self.fields['first_name'].required = False
        
        self.fields['last_name'].label="اسم المدرسه الرسمي"
        self.fields['last_name'].help_text = "سيتم استخدام هذا الاسم كاسم العرض للمدرسة."
        self.fields['last_name'].widget.attrs.update({'placeholder': 'مثال: مدرسة النهضة الحديثة'})

class UserLoginForm(AuthenticationForm):
    """
    فورم مخصص لتسجيل الدخول يرث من فورم Django المدمج.
    """
    username = forms.CharField(
        label="اسم المستخدم أو البريد الإلكتروني",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ادخل اسم المستخدم أو بريدك الإلكتروني'})
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'ادخل كلمة المرور'})
    )



# ===================================================================
# فورم جديد لتعديل بيانات المستخدم الأساسية (البريد ورقم الجوال)
# ===================================================================
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone_number'] # الحقول التي نريد تعديلها

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})

# ===================================================================
# فورم مخصص لتغيير كلمة المرور (بتنسيق Bootstrap)
# ===================================================================
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # =================== هذا هو التعديل الرئيسي ===================
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'كلمة المرور الحالية',
            'autocomplete': 'current-password' # إشارة للمتصفح
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'كلمة المرور الجديدة',
            'autocomplete': 'new-password' # إشارة للمتصفح
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'تأكيد كلمة المرور الجديدة',
            'autocomplete': 'new-password' # إشارة للمتصفح
        })