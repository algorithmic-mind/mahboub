from django.db import models
from django.core.exceptions import ValidationError


class SiteSettings(models.Model):
    """Singleton — فقط یک رکورد در پایگاه داده"""

    # ── هویت بصری ─────────────────────────────────────────────────────────
    site_name        = models.CharField(max_length=100, default="سامانه جامع محبوب", verbose_name="نام سایت")
    site_description = models.TextField(blank=True, verbose_name="توضیح کوتاه سایت (SEO)")
    logo             = models.ImageField(upload_to='settings/logo/', blank=True, verbose_name="لوگو اصلی")
    logo_dark        = models.ImageField(upload_to='settings/logo/', blank=True, verbose_name="لوگو حالت تاریک")
    favicon          = models.ImageField(upload_to='settings/favicon/', blank=True, verbose_name="Favicon")

    # ── تایپوگرافی ────────────────────────────────────────────────────────
    FONT_CHOICES = [
        ('Vazirmatn', 'وزیر متن'),
        ('Shabnam',   'شبنم'),
        ('Samim',     'صمیم'),
    ]
    font_primary   = models.CharField(max_length=50, choices=FONT_CHOICES, default='Vazirmatn', verbose_name="فونت اصلی")
    font_custom_url= models.URLField(blank=True, verbose_name="لینک فونت سفارشی (Google / CDN)")

    # ── رنگ‌بندی ──────────────────────────────────────────────────────────
    color_primary   = models.CharField(max_length=7, default='#f65b5b', verbose_name="رنگ اصلی (HEX)")
    color_secondary = models.CharField(max_length=7, default='#ff8c42', verbose_name="رنگ ثانویه (HEX)")
    color_accent    = models.CharField(max_length=7, default='#4a90d9', verbose_name="رنگ تاکید (HEX)")

    # ── اطلاعات تماس ──────────────────────────────────────────────────────
    email        = models.EmailField(blank=True, verbose_name="ایمیل پشتیبانی")
    phone        = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس")
    address      = models.TextField(blank=True, verbose_name="آدرس")
    telegram     = models.URLField(blank=True, verbose_name="لینک تلگرام")
    instagram    = models.URLField(blank=True, verbose_name="لینک اینستاگرام")
    whatsapp     = models.CharField(max_length=20, blank=True, verbose_name="شماره واتساپ")
    eitaa     = models.CharField(max_length=20, blank=True, verbose_name="لینک ایتا")
    bale    = models.CharField(max_length=20, blank=True, verbose_name="لینک بله")

    # ── SEO و اسکریپت‌ها ──────────────────────────────────────────────────
    meta_keywords       = models.CharField(max_length=500, blank=True, verbose_name="کلمات کلیدی SEO")
    google_analytics_id = models.CharField(max_length=30, blank=True, verbose_name="Google Analytics ID")
    head_scripts        = models.TextField(blank=True, verbose_name="اسکریپت‌های <head>")
    footer_scripts      = models.TextField(blank=True, verbose_name="اسکریپت‌های انتهای <body>")

    # ── پیام‌های سیستمی ────────────────────────────────────────────────────
    maintenance_mode    = models.BooleanField(default=False, verbose_name="حالت تعمیر و نگهداری")
    maintenance_message = models.TextField(blank=True, default="سایت در حال به‌روزرسانی است. لطفاً کمی بعد مراجعه کنید.", verbose_name="پیام تعمیر")
    ai_welcome_popup    = models.BooleanField(default=True, verbose_name="نمایش پاپ‌آپ هوش مصنوعی")
    footer_text         = models.TextField(blank=True, verbose_name="متن فوتر")
    copyright_text      = models.CharField(max_length=255, blank=True, verbose_name="متن کپی‌رایت")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return "تنظیمات سایت"

    def save(self, *args, **kwargs):
        """Singleton enforcement"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # حذف ممنوع

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ── اسلایدر ───────────────────────────────────────────────────────────────

class Slider(models.Model):
    class SliderPosition(models.TextChoices):
        HOME_TOP    = 'home_top',    'صفحه اصلی — بالا'
        HOME_MIDDLE = 'home_middle', 'صفحه اصلی — میانی'
        BOOKS       = 'books',       'صفحه کتاب‌ها'
        COURSES     = 'courses',     'صفحه نگاره‌ها'

    title       = models.CharField(max_length=100, verbose_name="نام اسلایدر")
    position    = models.CharField(max_length=20, choices=SliderPosition.choices, default=SliderPosition.HOME_TOP, verbose_name="محل نمایش")
    is_active   = models.BooleanField(default=True, verbose_name="فعال")
    auto_play   = models.BooleanField(default=True, verbose_name="پخش خودکار")
    interval    = models.PositiveSmallIntegerField(default=4000, verbose_name="فاصله پخش (ms)")

    class Meta:
        verbose_name = "اسلایدر"
        verbose_name_plural = "اسلایدرها"

    def __str__(self):
        return self.title


class SliderSlide(models.Model):
    slider      = models.ForeignKey(Slider, on_delete=models.CASCADE, related_name='slides', verbose_name="اسلایدر")
    title       = models.CharField(max_length=200, blank=True, verbose_name="عنوان اسلاید")
    subtitle    = models.CharField(max_length=300, blank=True, verbose_name="زیرعنوان")
    image       = models.ImageField(upload_to='settings/sliders/', verbose_name="تصویر")
    mobile_image= models.ImageField(upload_to='settings/sliders/mobile/', blank=True, verbose_name="تصویر موبایل")
    link        = models.URLField(blank=True, verbose_name="لینک اسلاید")
    link_text   = models.CharField(max_length=50, blank=True, verbose_name="متن دکمه")
    order       = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")
    is_active   = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "اسلاید"
        verbose_name_plural = "اسلایدها"
        ordering = ['order']

    def __str__(self):
        return f"{self.slider.title} — اسلاید {self.order}"


# ── بنر ──────────────────────────────────────────────────────────────────

class Banner(models.Model):
    class BannerPosition(models.TextChoices):
        SIDEBAR     = 'sidebar',     'سایدبار'
        HOME_BOTTOM = 'home_bottom', 'پایین صفحه اصلی'
        IN_CONTENT  = 'in_content',  'داخل محتوا'
        POPUP       = 'popup',       'پاپ‌آپ'

    title    = models.CharField(max_length=100, verbose_name="نام بنر")
    image    = models.ImageField(upload_to='settings/banners/', verbose_name="تصویر بنر")
    link     = models.URLField(blank=True, verbose_name="لینک")
    position = models.CharField(max_length=20, choices=BannerPosition.choices, verbose_name="موقعیت")
    is_active= models.BooleanField(default=True, verbose_name="فعال")
    order    = models.PositiveSmallIntegerField(default=0)
    starts_at= models.DateTimeField(null=True, blank=True, verbose_name="شروع نمایش")
    ends_at  = models.DateTimeField(null=True, blank=True, verbose_name="پایان نمایش")

    class Meta:
        verbose_name = "بنر"
        verbose_name_plural = "بنرها"
        ordering = ['position', 'order']

    def __str__(self):
        return self.title


# ── منوی ناوبری ──────────────────────────────────────────────────────────

class MenuItem(models.Model):
    class MenuLocation(models.TextChoices):
        HEADER  = 'header',  'هدر / منوی کشویی'
        FOOTER  = 'footer',  'فوتر'
        BOTTOM  = 'bottom',  'نوار پایین (موبایل)'

    label    = models.CharField(max_length=80, verbose_name="عنوان آیتم")
    url      = models.CharField(max_length=200, verbose_name="لینک / URL")
    icon     = models.CharField(max_length=50, blank=True, verbose_name="آیکون Font Awesome")
    location = models.CharField(max_length=10, choices=MenuLocation.choices, default=MenuLocation.HEADER, verbose_name="محل نمایش")
    parent   = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name="والد"
    )
    order     = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    open_new_tab = models.BooleanField(default=False, verbose_name="باز در تب جدید")

    class Meta:
        verbose_name = "آیتم منو"
        verbose_name_plural = "آیتم‌های منو"
        ordering = ['location', 'order']

    def __str__(self):
        return f"[{self.get_location_display()}] {self.label}"