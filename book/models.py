from django.db import models


# ══════════════════════════════════════════════════════════════════════════
#  دسته‌بندی کتاب
# ══════════════════════════════════════════════════════════════════════════

class BookCategory(models.Model):
    name   = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug   = models.SlugField(unique=True, allow_unicode=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name="دسته‌بندی والد"
    )
    icon  = models.CharField(max_length=50, blank=True, verbose_name="آیکون (Font Awesome)")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name        = "دسته‌بندی کتاب"
        verbose_name_plural = "دسته‌بندی‌های کتاب"
        ordering            = ['order', 'name']

    def __str__(self):
        return self.name


# ══════════════════════════════════════════════════════════════════════════
#  کتاب  (متادیتا + قیمت‌گذاری)
# ══════════════════════════════════════════════════════════════════════════

class Book(models.Model):

    class AccessType(models.TextChoices):
        FREE    = 'free',    'رایگان'
        PAID    = 'paid',    'پولی'
        PREMIUM = 'premium', 'اشتراکی (ویژه اعضا)'

    # ── اطلاعات اصلی ──────────────────────────────────────────────────────
    title       = models.CharField(max_length=255, verbose_name="عنوان کتاب")
    slug        = models.SlugField(unique=True, allow_unicode=True)
    author      = models.CharField(max_length=255, verbose_name="نویسنده / مولف")
    translator  = models.CharField(max_length=255, blank=True, verbose_name="مترجم")
    publisher   = models.CharField(max_length=255, blank=True, verbose_name="ناشر")
    description = models.TextField(blank=True, verbose_name="توضیحات / معرفی کتاب")
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, verbose_name="تصویر جلد")

    # ── دسته‌بندی ──────────────────────────────────────────────────────────
    category = models.ForeignKey(
        BookCategory, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='books',
        verbose_name="دسته‌بندی"
    )

    # ── دسترسی و قیمت ─────────────────────────────────────────────────────
    access_type      = models.CharField(
        max_length=20, choices=AccessType.choices,
        default=AccessType.FREE, verbose_name="نوع دسترسی"
    )
    price            = models.PositiveIntegerField(default=0, verbose_name="قیمت (تومان)")
    discount_percent = models.PositiveSmallIntegerField(default=0, verbose_name="درصد تخفیف")

    # ── مشخصات کتاب ───────────────────────────────────────────────────────
    volume       = models.PositiveSmallIntegerField(default=1, verbose_name="جلد / قسمت")
    isbn         = models.CharField(max_length=20, blank=True, verbose_name="شابک (ISBN)")
    language     = models.CharField(max_length=30, default='فارسی', verbose_name="زبان")
    publish_year = models.CharField(max_length=10, blank=True, verbose_name="سال انتشار")

    # ── آمار ──────────────────────────────────────────────────────────────
    views  = models.PositiveIntegerField(default=0, verbose_name="بازدید")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name="امتیاز")

    # ── وضعیت ─────────────────────────────────────────────────────────────
    is_active   = models.BooleanField(default=True,  verbose_name="فعال")
    is_featured = models.BooleanField(default=False, verbose_name="ویژه / پیشنهادی")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "کتاب"
        verbose_name_plural = "کتاب‌ها"
        ordering            = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        return int(self.price * (1 - self.discount_percent / 100))

    @property
    def total_pages(self):
        return self.pages.count()

    @property
    def total_chapters(self):
        return self.chapters.count()


# ══════════════════════════════════════════════════════════════════════════
#  فصل  (ساختار منطقی کتاب)
# ══════════════════════════════════════════════════════════════════════════

class BookChapter(models.Model):
    book  = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name="کتاب"
    )
    title = models.CharField(max_length=255, verbose_name="عنوان فصل")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب فصل")
    is_preview = models.BooleanField(
        default=False,
        verbose_name="پیش‌نمایش رایگان",
        help_text="اگر فعال باشد، صفحات این فصل برای همه کاربران (بدون خرید) قابل خواندن است."
    )

    class Meta:
        verbose_name        = "فصل کتاب"
        verbose_name_plural = "فصل‌های کتاب"
        ordering            = ['order']
        unique_together     = [('book', 'order')]

    def __str__(self):
        return f"{self.book.title} ← فصل {self.order}: {self.title}"

    @property
    def pages_count(self):
        return self.pages.count()


# ══════════════════════════════════════════════════════════════════════════
#  صفحه  (واحد اصلی ذخیره محتوا در دیتابیس)
# ══════════════════════════════════════════════════════════════════════════

class BookPage(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        related_name='pages',
        verbose_name="کتاب"
    )
    chapter = models.ForeignKey(
        BookChapter, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pages',
        verbose_name="فصل"
    )

    # ── شماره‌گذاری ───────────────────────────────────────────────────────
    # page_number : شماره چاپی (همانطور که در کتاب اصلی بوده — ممکن است رشته باشد مثل "i, ii")
    # order       : ترتیب واقعی در DB برای ناوبری (همیشه عدد صحیح)
    page_number = models.CharField(
        max_length=10,
        verbose_name="شماره صفحه (چاپی)",
        help_text="شماره‌ای که در کتاب اصلی است، مثلاً ۱، ۲ یا i، ii برای مقدمه"
    )
    order = models.PositiveIntegerField(
        verbose_name="ترتیب نمایش",
        db_index=True,
        help_text="ترتیب واقعی صفحه در سیستم — برای ناوبری قبلی/بعدی استفاده می‌شود"
    )

    # ── محتوا ─────────────────────────────────────────────────────────────
    content = models.TextField(
        verbose_name="متن صفحه",
        help_text="متن کامل این صفحه. HTML ساده مجاز است."
    )

    # ── عنوان میانی ───────────────────────────────────────────────────────
    # فقط وقتی صفحه شروع یک بخش/مبحث جدید است پر می‌شود
    heading = models.CharField(
        max_length=255, blank=True,
        verbose_name="عنوان میانی",
        help_text="اگر این صفحه شروع یک مبحث جدید است، عنوان آن را وارد کنید."
    )

    # ── تصویر صفحه (اختیاری) ─────────────────────────────────────────────
    # برای کتاب‌هایی که علاوه بر متن، اسکن تصویری هم دارند
    page_image = models.ImageField(
        upload_to='books/pages/',
        blank=True,
        verbose_name="تصویر صفحه",
        help_text="اختیاری — مثلاً اسکن صفحه اصلی یا تصویر مرتبط"
    )

    # ── یادداشت ویراستار ──────────────────────────────────────────────────
    editor_note = models.TextField(
        blank=True,
        verbose_name="یادداشت ویراستار",
        help_text="داخلی — برای کاربر نمایش داده نمی‌شود."
    )

    class Meta:
        verbose_name        = "صفحه کتاب"
        verbose_name_plural = "صفحات کتاب"
        ordering            = ['order']
        unique_together     = [('book', 'order')]
        indexes             = [
            models.Index(fields=['book', 'order']),
            models.Index(fields=['book', 'chapter']),
        ]

    def __str__(self):
        return f"{self.book.title} — ص {self.page_number}"

    # ── ناوبری صفحه به صفحه ──────────────────────────────────────────────
    def next_page(self):
        return BookPage.objects.filter(
            book=self.book, order=self.order + 1
        ).first()

    def prev_page(self):
        return BookPage.objects.filter(
            book=self.book, order=self.order - 1
        ).first()