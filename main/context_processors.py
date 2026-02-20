# main/context_processors.py
from .models import SiteSettings

def site_settings(request):
    """اضافه کردن تنظیمات سایت به همه قالب‌ها"""
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None
    
    return {
        'site_settings': settings
    }