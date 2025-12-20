# في dashboard/decorators.py

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    """
    ديكوريتور يتأكد من أن المستخدم عضو في مجموعة 'Admins'.
    """
    def check_is_admin(user):
        if user.is_authenticated and (user.is_superuser or user.groups.filter(name='Admins').exists()):
            return True
        raise PermissionDenied
    
    # استخدام الديكوريتور الجاهز user_passes_test مع دالتنا المخصصة
    return user_passes_test(check_is_admin)(view_func)
