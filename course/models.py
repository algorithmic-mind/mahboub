from django.db import models
from django.contrib.auth.models import User


class CourseCategory(models.Model):
    name   = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug   = models.SlugField(unique=True, allow_unicode=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name="دسته‌بندی والد"
    )
    icon  = models.CharField(max_length=50, blank=True, verbose_name="آیکون")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "دسته‌بندی نگاره"
        verbose_name_plural = "دسته‌بندی‌های نگاره"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Course(models.Model):
    class AccessType(models.TextChoices):
        FREE    = 'free',    'رایگان'
        PAID    = 'paid',    'پولی'
        PREMIUM = 'premium', 'اشتراکی'

    class Level(models.TextChoices):
        BEGINNER     = 'beginner',     'مبتدی'
        INTERMEDIATE = 'intermediate', 'متوسط'
        ADVANCED     = 'advanced',     'پیشرفته'
        ALL          = 'all',          'همه سطوح'

    # ── اطلاعات اصلی ──────────────────────────────────────────────────────
    title       = models.CharField(max_length=255, verbose_name="عنوان دوره")
    slug        = models.SlugField(unique=True, allow_unicode=True)
    instructor  = models.CharField(max_length=255, verbose_name="استاد / مدرس")
    category    = models.ForeignKey(
        CourseCategory, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='courses',
        verbose_name="دسته‌بندی"
    )
    description     = models.TextField(blank=True, verbose_name="توضیحات")
    short_desc      = models.CharField(max_length=500, blank=True, verbose_name="توضیح کوتاه")
    cover_image     = models.ImageField(upload_to='courses/covers/', blank=True, verbose_name="تصویر کاور")
    intro_video_url = models.URLField(blank=True, verbose_name="لینک ویدیو معرفی")

    # ── دسترسی و قیمت ─────────────────────────────────────────────────────
    access_type      = models.CharField(max_length=20, choices=AccessType.choices, default=AccessType.FREE, verbose_name="نوع دسترسی")
    price            = models.PositiveIntegerField(default=0, verbose_name="قیمت (تومان)")
    discount_percent = models.PositiveSmallIntegerField(default=0, verbose_name="درصد تخفیف")

    # ── مشخصات دوره ───────────────────────────────────────────────────────
    level           = models.CharField(max_length=20, choices=Level.choices, default=Level.ALL, verbose_name="سطح دوره")
    total_duration  = models.PositiveIntegerField(default=0, verbose_name="مدت کل (دقیقه)")
    lessons_count   = models.PositiveSmallIntegerField(default=0, verbose_name="تعداد درس")
    has_certificate = models.BooleanField(default=False, verbose_name="دارای گواهینامه")

    # ── آمار ──────────────────────────────────────────────────────────────
    views        = models.PositiveIntegerField(default=0, verbose_name="بازدید")
    enrollments  = models.PositiveIntegerField(default=0, verbose_name="ثبت‌نام")
    rating       = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name="امتیاز")

    # ── وضعیت ─────────────────────────────────────────────────────────────
    is_active   = models.BooleanField(default=True, verbose_name="فعال")
    is_featured = models.BooleanField(default=False, verbose_name="ویژه")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "نگاره (دوره ویدیویی)"
        verbose_name_plural = "نگاره‌ها (دوره‌های ویدیویی)"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        return int(self.price * (1 - self.discount_percent / 100))

    @property
    def duration_display(self):
        h, m = divmod(self.total_duration, 60)
        return f"{h} ساعت {m} دقیقه" if h else f"{m} دقیقه"


class CourseSection(models.Model):
    """فصل / بخش داخل یک دوره"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections', verbose_name="دوره")
    title  = models.CharField(max_length=255, verbose_name="عنوان بخش")
    order  = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "بخش دوره"
        verbose_name_plural = "بخش‌های دوره"
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class CourseLesson(models.Model):
    class LessonType(models.TextChoices):
        VIDEO    = 'video',    'ویدیو'
        AUDIO    = 'audio',    'صوت'
        PDF      = 'pdf',      'PDF'
        TEXT     = 'text',     'متن'
        QUIZ     = 'quiz',     'آزمون'

    section     = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name='lessons', verbose_name="بخش")
    title       = models.CharField(max_length=255, verbose_name="عنوان درس")
    lesson_type = models.CharField(max_length=10, choices=LessonType.choices, default=LessonType.VIDEO, verbose_name="نوع محتوا")
    video_url   = models.URLField(blank=True, verbose_name="لینک ویدیو")
    video_file  = models.FileField(upload_to='courses/videos/', blank=True, verbose_name="فایل ویدیو")
    duration    = models.PositiveIntegerField(default=0, verbose_name="مدت زمان (ثانیه)")
    is_preview  = models.BooleanField(default=False, verbose_name="پیش‌نمایش رایگان")
    order       = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "درس‌ها"
        ordering = ['order']

    def __str__(self):
        return self.title