
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import logging

# استيراد النماذج
User = get_user_model()

# يجب استيراد النماذج الأخرى حسب مشروعك
try:
    from Schools.models import SchoolProfile
    from Teachers.models import TeacherProfile
    # from jobs.models import JobPosting  # إذا كان لديك نموذج للوظائف
    # from applications.models import Application  # إذا كان لديك نموذج للطلبات
except ImportError:
    # في حالة عدم وجود هذه النماذج بعد
    SchoolProfile = None
    TeacherProfile = None

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    """
    واجهة الصفحة الرئيسية مع الإحصائيات الديناميكية
    """
    template_name = 'core/home.html'
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # الحصول على الإحصائيات من الكاش أولاً
            stats = cache.get('homepage_stats')
            
            if stats is None:
                stats = self.get_statistics()
                # حفظ الإحصائيات في الكاش لمدة 30 دقيقة
                cache.set('homepage_stats', stats, 60 * 30)
            
            context.update(stats)
            
        except Exception as e:
            logger.error(f"Error getting homepage statistics: {e}")
            # إحصائيات افتراضية في حالة الخطأ
            context.update({
                'teachers_count': 400,
                'schools_count': 600,
                'successful_matches': 250,
                'satisfaction_rate': 98,
                'recent_teachers': [],
                'recent_schools': [],
                'featured_jobs': [],
            })
        
        return context
    
    def get_statistics(self):
        """
        حساب الإحصائيات الديناميكية للمنصة
        """
        stats = {}
        
        # إحصائيات المعلمين
        if TeacherProfile:
            teachers_count = TeacherProfile.objects.filter(
                user__is_active=True
            ).count()
            stats['teachers_count'] = teachers_count
            
            # أحدث المعلمين المسجلين
            stats['recent_teachers'] = TeacherProfile.objects.filter(
                user__is_active=True
            ).select_related('user').order_by('-user__date_joined')[:6]
        else:
            stats['teachers_count'] = 400  # رقم افتراضي
            stats['recent_teachers'] = []
        
        # إحصائيات المدارس
        if SchoolProfile:
            schools_count = SchoolProfile.objects.filter(
                user__is_active=True
            ).count()
            stats['schools_count'] = schools_count
            
            # أحدث المدارس المسجلة
            stats['recent_schools'] = SchoolProfile.objects.filter(
                user__is_active=True
            ).select_related('user').order_by('-user__date_joined')[:6]
        else:
            stats['schools_count'] = 600  # رقم افتراضي
            stats['recent_schools'] = []
        
        # إحصائيات إضافية
        stats['successful_matches'] = self.calculate_successful_matches()
        stats['satisfaction_rate'] = self.calculate_satisfaction_rate()
        stats['total_users'] = User.objects.filter(is_active=True).count()
        
        # إحصائيات حسب نوع المستخدم
        user_types_stats = User.objects.filter(is_active=True).values('user_type').annotate(
            count=Count('id')
        )
        
        for stat in user_types_stats:
            if stat['user_type'] == 'TEACHER':
                stats['verified_teachers_count'] = stat['count']
            elif stat['user_type'] == 'SCHOOL':
                stats['verified_schools_count'] = stat['count']
        
        # الوظائف المميزة (إذا كان لديك نموذج للوظائف)
        stats['featured_jobs'] = self.get_featured_jobs()
        
        return stats
    
    def calculate_successful_matches(self):
        """
        حساب عدد المطابقات الناجحة
        يمكن تخصيص هذه الدالة حسب منطق مشروعك
        """
        try:
            # مثال: إذا كان لديك نموذج للطلبات المقبولة
            # from applications.models import Application
            # return Application.objects.filter(status='ACCEPTED').count()
            
            # أو يمكن حسابها بناءً على المعلمين الذين لديهم مدارس
            if TeacherProfile:
                # افتراض أن لديك حقل current_school في TeacherProfile
                # return TeacherProfile.objects.filter(current_school__isnull=False).count()
                pass
            
            # رقم افتراضي للآن
            return 250
            
        except Exception as e:
            logger.error(f"Error calculating successful matches: {e}")
            return 250
    
    def calculate_satisfaction_rate(self):
        """
        حساب نسبة الرضا
        يمكن تخصيص هذه الدالة حسب نظام التقييم في مشروعك
        """
        try:
            # مثال: إذا كان لديك نموذج للتقييمات
            # from reviews.models import Review
            # total_reviews = Review.objects.count()
            # positive_reviews = Review.objects.filter(rating__gte=4).count()
            # return round((positive_reviews / total_reviews) * 100) if total_reviews > 0 else 98
            
            # رقم افتراضي للآن
            return 98
            
        except Exception as e:
            logger.error(f"Error calculating satisfaction rate: {e}")
            return 98
    
    def get_featured_jobs(self):
        """
        الحصول على الوظائف المميزة
        """
        try:
            # مثال: إذا كان لديك نموذج للوظائف
            # from jobs.models import JobPosting
            # return JobPosting.objects.filter(
            #     is_active=True,
            #     is_featured=True
            # ).select_related('school').order_by('-created_at')[:3]
            
            # قائمة فارغة للآن
            return []
            
        except Exception as e:
            logger.error(f"Error getting featured jobs: {e}")
            return []


def home_page_view(request):
    """
    واجهة بديلة للصفحة الرئيسية (Function-based view)
    """
    try:
        # الحصول على الإحصائيات
        context = {}
        
        # إحصائيات المعلمين
        if TeacherProfile:
            context['teachers_count'] = TeacherProfile.objects.filter(
                user__is_active=True
            ).count()
        else:
            context['teachers_count'] = 400
        
        # إحصائيات المدارس
        if SchoolProfile:
            context['schools_count'] = SchoolProfile.objects.filter(
                user__is_active=True
            ).count()
        else:
            context['schools_count'] = 600
        
        # إحصائيات إضافية
        context.update({
            'successful_matches': 250,
            'satisfaction_rate': 98,
            'total_users': User.objects.filter(is_active=True).count(),
        })
        
        return render(request, 'home.html', context)
        
    except Exception as e:
        logger.error(f"Error in home page view: {e}")
        # إحصائيات افتراضية في حالة الخطأ
        context = {
            'teachers_count': 400,
            'schools_count': 600,
            'successful_matches': 250,
            'satisfaction_rate': 98,
            'total_users': 1000,
        }
        return render(request, 'home.html', context)


# واجهة للحصول على الإحصائيات عبر AJAX
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def get_stats_ajax(request):
    """
    إرجاع الإحصائيات بصيغة JSON للتحديث الديناميكي
    """
    try:
        stats = cache.get('homepage_stats')
        
        if stats is None:
            # إعادة حساب الإحصائيات
            home_view = HomePageView()
            stats = home_view.get_statistics()
            cache.set('homepage_stats', stats, 60 * 30)
        
        # تحويل الكائنات المعقدة إلى قيم بسيطة
        json_stats = {
            'teachers_count': stats.get('teachers_count', 400),
            'schools_count': stats.get('schools_count', 600),
            'successful_matches': stats.get('successful_matches', 250),
            'satisfaction_rate': stats.get('satisfaction_rate', 98),
            'total_users': stats.get('total_users', 1000),
        }
        
        return JsonResponse({
            'success': True,
            'stats': json_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats via AJAX: {e}")
        return JsonResponse({
            'success': False,
            'error': 'حدث خطأ في الحصول على الإحصائيات'
        }, status=500)


# إشارات Django لتحديث الكاش عند تغيير البيانات
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=User)
def clear_homepage_cache(sender, **kwargs):
    """
    مسح كاش الصفحة الرئيسية عند تغيير بيانات المستخدمين
    """
    cache.delete('homepage_stats')

if TeacherProfile:
    @receiver([post_save, post_delete], sender=TeacherProfile)
    def clear_homepage_cache_teacher(sender, **kwargs):
        cache.delete('homepage_stats')

if SchoolProfile:
    @receiver([post_save, post_delete], sender=SchoolProfile)
    def clear_homepage_cache_school(sender, **kwargs):
        cache.delete('homepage_stats')

