from django.db import models


class PodcastCategory(models.Model):
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
        verbose_name = "دسته‌بندی پادکست"
        verbose_name_plural = "دسته‌بندی‌های پادکست"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class PodcastSeries(models.Model):
    """یک مجموعه یا فصل پادکست — مثلاً «درس اخلاق استاد پناهیان»"""
    title       = models.CharField(max_length=255, verbose_name="عنوان مجموعه")
    slug        = models.SlugField(unique=True, allow_unicode=True)
    host        = models.CharField(max_length=255, verbose_name="گوینده / استاد")
    category    = models.ForeignKey(
        PodcastCategory, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='series',
        verbose_name="دسته‌بندی"
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")
    cover_image = models.ImageField(upload_to='podcasts/covers/', blank=True, verbose_name="تصویر کاور")
    is_active   = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, verbose_name="ویژه")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مجموعه پادکست"
        verbose_name_plural = "مجموعه‌های پادکست"

    def __str__(self):
        return self.title


class Podcast(models.Model):
    class AccessType(models.TextChoices):
        FREE    = 'free',    'رایگان'
        PAID    = 'paid',    'پولی'
        PREMIUM = 'premium', 'اشتراکی'

    # ── اطلاعات اصلی ──────────────────────────────────────────────────────
    title       = models.CharField(max_length=255, verbose_name="عنوان قسمت")
    slug        = models.SlugField(unique=True, allow_unicode=True)
    series      = models.ForeignKey(
        PodcastSeries, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='episodes',
        verbose_name="مجموعه"
    )
    category    = models.ForeignKey(
        PodcastCategory, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='podcasts',
        verbose_name="دسته‌بندی"
    )
    host        = models.CharField(max_length=255, blank=True, verbose_name="گوینده / استاد")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    cover_image = models.ImageField(upload_to='podcasts/covers/', blank=True, verbose_name="تصویر کاور")

    # ── فایل صوتی ─────────────────────────────────────────────────────────
    audio_file  = models.FileField(upload_to='podcasts/audio/', blank=True, verbose_name="فایل صوتی")
    audio_url   = models.URLField(blank=True, verbose_name="لینک خارجی صوت (CDN)")
    duration    = models.PositiveIntegerField(default=0, verbose_name="مدت زمان (ثانیه)")

    # ── دسترسی و قیمت ─────────────────────────────────────────────────────
    access_type     = models.CharField(max_length=20, choices=AccessType.choices, default=AccessType.FREE, verbose_name="نوع دسترسی")
    price           = models.PositiveIntegerField(default=0, verbose_name="قیمت (تومان)")
    discount_percent= models.PositiveSmallIntegerField(default=0, verbose_name="درصد تخفیف")

    # ── ترتیب در مجموعه ───────────────────────────────────────────────────
    episode_number  = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="شماره قسمت")

    # ── آمار ──────────────────────────────────────────────────────────────
    plays       = models.PositiveIntegerField(default=0, verbose_name="تعداد پخش")
    downloads   = models.PositiveIntegerField(default=0, verbose_name="دانلود")
    rating      = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name="امتیاز")

    # ── وضعیت ─────────────────────────────────────────────────────────────
    is_active   = models.BooleanField(default=True, verbose_name="فعال")
    is_featured = models.BooleanField(default=False, verbose_name="ویژه")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "پادکست"
        verbose_name_plural = "پادکست‌ها"
        ordering = ['series', 'episode_number', '-created_at']

    def __str__(self):
        return self.title

    @property
    def duration_display(self):
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

    @property
    def final_price(self):
        return int(self.price * (1 - self.discount_percent / 100))