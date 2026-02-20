from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Max
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import BookCategory, Book, BookChapter, BookPage


# ══════════════════════════════════════════════════════════════════════════
#  دسته‌بندی
# ══════════════════════════════════════════════════════════════════════════

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'parent', 'icon_preview', 'order', 'books_count')
    list_editable = ('order',)
    list_filter   = ('parent',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{}"></i>&ensp;<small style="color:#888;">{}</small>', obj.icon, obj.icon)
        return '—'
    icon_preview.short_description = 'آیکون'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_count=Count('books'))

    def books_count(self, obj):
        return obj._count
    books_count.short_description = 'تعداد کتاب'
    books_count.admin_order_field = '_count'


# ══════════════════════════════════════════════════════════════════════════
#  Inline: فصل‌ها داخل کتاب
# ══════════════════════════════════════════════════════════════════════════

class BookChapterInline(admin.TabularInline):
    model   = BookChapter
    extra   = 1
    fields  = ('order', 'title', 'is_preview', 'pages_count_display')
    readonly_fields = ('pages_count_display',)
    ordering = ('order',)
    show_change_link = True

    def pages_count_display(self, obj):
        if obj.pk:
            count = obj.pages.count()
            url = (
                reverse('admin:book_bookpage_changelist')
                + f'?chapter__id__exact={obj.pk}'
            )
            return format_html('<a href="{}">{} صفحه</a>', url, count)
        return '—'
    pages_count_display.short_description = 'تعداد صفحه'


# ══════════════════════════════════════════════════════════════════════════
#  کتاب
# ══════════════════════════════════════════════════════════════════════════

class AccessTypeFilter(admin.SimpleListFilter):
    title = 'نوع دسترسی'
    parameter_name = 'access_type'

    def lookups(self, request, model_admin):
        return Book.AccessType.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(access_type=self.value())
        return queryset


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'cover_thumbnail', 'title', 'author', 'category',
        'access_badge', 'price_display',
        'chapters_count', 'pages_count',
        'views', 'rating',
        'is_featured', 'is_active',
    )
    list_display_links = ('cover_thumbnail', 'title')
    list_editable      = ('is_featured', 'is_active')
    list_filter        = (AccessTypeFilter, 'category', 'language', 'is_active', 'is_featured')
    search_fields      = ('title', 'author', 'publisher', 'isbn')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields    = (
        'views', 'created_at', 'updated_at',
        'cover_preview', 'content_summary',
    )
    list_per_page  = 20
    date_hierarchy = 'created_at'
    save_on_top    = True
    inlines        = [BookChapterInline]

    fieldsets = (
        ('📖  اطلاعات کتاب', {
            'fields': (
                'title', 'slug', 'author', 'translator',
                'publisher', 'description',
            ),
        }),
        ('🖼️  جلد', {
            'fields': ('cover_image', 'cover_preview'),
            'classes': ('collapse',),
        }),
        ('🗂️  دسته‌بندی', {
            'fields': ('category',),
        }),
        ('💰  دسترسی و قیمت', {
            'fields': ('access_type', 'price', 'discount_percent'),
        }),
        ('📋  مشخصات', {
            'fields': ('volume', 'isbn', 'language', 'publish_year'),
        }),
        ('✅  وضعیت نمایش', {
            'fields': ('is_active', 'is_featured'),
        }),
        ('📊  آمار (فقط نمایش)', {
            'fields': ('views', 'rating', 'content_summary', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # ── تصویر جلد ─────────────────────────────────────────────────────────
    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width:40px;height:54px;object-fit:cover;border-radius:4px;box-shadow:0 1px 4px #0003;"/>',
                obj.cover_image.url
            )
        return format_html(
            '<div style="width:40px;height:54px;background:#f0f0f0;border-radius:4px;'
            'display:flex;align-items:center;justify-content:center;font-size:20px;">📚</div>'
        )
    cover_thumbnail.short_description = 'جلد'

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:220px;border-radius:8px;box-shadow:0 2px 8px #0002;"/>',
                obj.cover_image.url
            )
        return '(تصویر جلد آپلود نشده)'
    cover_preview.short_description = 'پیش‌نمایش جلد'

    # ── badge دسترسی ──────────────────────────────────────────────────────
    def access_badge(self, obj):
        colors = {'free': '#198754', 'paid': '#dc3545', 'premium': '#6f42c1'}
        color  = colors.get(obj.access_type, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_access_type_display()
        )
    access_badge.short_description = 'دسترسی'

    def price_display(self, obj):
        if obj.access_type == 'free':
            return format_html('<span style="color:#198754;font-weight:bold;">رایگان</span>')
        p = obj.final_price
        if obj.discount_percent:
            return format_html(
                '<span style="color:#dc3545;font-weight:bold;">{:,}</span>'
                '&ensp;<small style="text-decoration:line-through;color:#999;">{:,}</small>'
                '&ensp;<small style="color:#fd7e14;">{}٪ تخفیف</small>',
                p, obj.price, obj.discount_percent
            )
        return format_html('{:,} تومان', p)
    price_display.short_description = 'قیمت'

    # ── آمار محتوا ────────────────────────────────────────────────────────
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _chapters=Count('chapters', distinct=True),
            _pages=Count('pages', distinct=True),
        )

    def chapters_count(self, obj):
        url = reverse('admin:book_bookchapter_changelist') + f'?book__id__exact={obj.pk}'
        return format_html('<a href="{}">{} فصل</a>', url, obj._chapters)
    chapters_count.short_description = 'فصل‌ها'
    chapters_count.admin_order_field = '_chapters'

    def pages_count(self, obj):
        url = reverse('admin:book_bookpage_changelist') + f'?book__id__exact={obj.pk}'
        return format_html('<a href="{}">{} صفحه</a>', url, obj._pages)
    pages_count.short_description = 'صفحات'
    pages_count.admin_order_field = '_pages'

    def content_summary(self, obj):
        chapters = obj.chapters.count()
        pages    = obj.pages.count()
        last_page = obj.pages.aggregate(m=Max('order'))['m'] or 0
        return format_html(
            '<table style="border-collapse:collapse;font-size:13px;">'
            '<tr><td style="padding:4px 12px 4px 0;color:#666;">تعداد فصل‌ها:</td><td><b>{}</b></td></tr>'
            '<tr><td style="padding:4px 12px 4px 0;color:#666;">تعداد صفحات:</td><td><b>{}</b></td></tr>'
            '<tr><td style="padding:4px 12px 4px 0;color:#666;">آخرین شماره ترتیب:</td><td><b>{}</b></td></tr>'
            '</table>',
            chapters, pages, last_page
        )
    content_summary.short_description = 'خلاصه محتوا'


# ══════════════════════════════════════════════════════════════════════════
#  فصل
# ══════════════════════════════════════════════════════════════════════════

class BookPageInline(admin.TabularInline):
    """نمایش فشرده صفحات داخل فصل"""
    model   = BookPage
    extra   = 0
    fields  = ('order', 'page_number', 'heading', 'content_preview', 'page_image')
    readonly_fields = ('content_preview',)
    ordering = ('order',)
    show_change_link = True

    def content_preview(self, obj):
        if obj.content:
            preview = obj.content[:80].replace('\n', ' ')
            return format_html(
                '<span style="color:#555;font-size:12px;">{}{}</span>',
                preview,
                '…' if len(obj.content) > 80 else ''
            )
        return '—'
    content_preview.short_description = 'پیش‌نمایش متن'


@admin.register(BookChapter)
class BookChapterAdmin(admin.ModelAdmin):
    list_display  = ('title', 'book_link', 'order', 'is_preview', 'pages_count_display')
    list_editable = ('order', 'is_preview')
    list_filter   = ('book', 'is_preview')
    search_fields = ('title', 'book__title')
    ordering      = ('book', 'order')
    inlines       = [BookPageInline]
    save_on_top   = True

    fieldsets = (
        ('اطلاعات فصل', {
            'fields': ('book', 'title', 'order', 'is_preview'),
        }),
    )

    def book_link(self, obj):
        url = reverse('admin:book_book_change', args=[obj.book.pk])
        return format_html('<a href="{}">{}</a>', url, obj.book.title)
    book_link.short_description = 'کتاب'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_pages=Count('pages'))

    def pages_count_display(self, obj):
        url = reverse('admin:book_bookpage_changelist') + f'?chapter__id__exact={obj.pk}'
        return format_html('<a href="{}">{} صفحه</a>', url, obj._pages)
    pages_count_display.short_description = 'صفحات'
    pages_count_display.admin_order_field = '_pages'


# ══════════════════════════════════════════════════════════════════════════
#  صفحه
# ══════════════════════════════════════════════════════════════════════════

@admin.register(BookPage)
class BookPageAdmin(admin.ModelAdmin):
    list_display  = (
        'book_link', 'chapter_link', 'page_number', 'order',
        'heading_display', 'content_preview', 'has_image',
    )
    list_filter   = ('book', 'chapter')
    search_fields = ('book__title', 'chapter__title', 'content', 'heading', 'page_number')
    ordering      = ('book', 'order')
    list_per_page = 30
    save_on_top   = True

    readonly_fields = ('nav_links', 'page_image_preview')

    fieldsets = (
        ('📌  موقعیت صفحه', {
            'fields': ('book', 'chapter', 'order', 'page_number'),
        }),
        ('📝  محتوا', {
            'fields': ('heading', 'content'),
        }),
        ('🖼️  تصویر صفحه', {
            'fields': ('page_image', 'page_image_preview'),
            'classes': ('collapse',),
        }),
        ('📋  یادداشت', {
            'fields': ('editor_note',),
            'classes': ('collapse',),
        }),
        ('🔗  ناوبری', {
            'fields': ('nav_links',),
            'classes': ('collapse',),
        }),
    )

    # ── ستون‌های لیست ─────────────────────────────────────────────────────
    def book_link(self, obj):
        url = reverse('admin:book_book_change', args=[obj.book.pk])
        return format_html('<a href="{}">{}</a>', url, obj.book.title)
    book_link.short_description = 'کتاب'
    book_link.admin_order_field = 'book__title'

    def chapter_link(self, obj):
        if obj.chapter:
            url = reverse('admin:book_bookchapter_change', args=[obj.chapter.pk])
            return format_html('<a href="{}">{}</a>', url, obj.chapter.title)
        return format_html('<span style="color:#aaa;">— بدون فصل —</span>')
    chapter_link.short_description = 'فصل'

    def heading_display(self, obj):
        if obj.heading:
            return format_html(
                '<span style="font-weight:600;color:#0d6efd;">{}</span>', obj.heading
            )
        return '—'
    heading_display.short_description = 'عنوان میانی'

    def content_preview(self, obj):
        if obj.content:
            preview = obj.content[:100].replace('\n', ' ')
            return format_html(
                '<span style="font-size:12px;color:#444;">{}{}</span>',
                preview,
                '…' if len(obj.content) > 100 else ''
            )
        return format_html('<span style="color:#ccc;">خالی</span>')
    content_preview.short_description = 'پیش‌نمایش متن'

    def has_image(self, obj):
        if obj.page_image:
            return format_html('<span style="color:#198754;font-size:16px;">✔</span>')
        return format_html('<span style="color:#ddd;">—</span>')
    has_image.short_description = 'تصویر'

    # ── فیلدهای فرم ───────────────────────────────────────────────────────
    def page_image_preview(self, obj):
        if obj.page_image:
            return format_html(
                '<img src="{}" style="max-width:300px;border-radius:6px;box-shadow:0 1px 6px #0002;"/>',
                obj.page_image.url
            )
        return '(تصویری آپلود نشده)'
    page_image_preview.short_description = 'پیش‌نمایش تصویر'

    def nav_links(self, obj):
        if not obj.pk:
            return '—'
        prev_p = obj.prev_page()
        next_p = obj.next_page()
        parts  = []
        if prev_p:
            url = reverse('admin:book_bookpage_change', args=[prev_p.pk])
            parts.append(format_html('← <a href="{}">صفحه قبل (ص {})</a>', url, prev_p.page_number))
        else:
            parts.append(format_html('<span style="color:#ccc;">← اول کتاب</span>'))
        if next_p:
            url = reverse('admin:book_bookpage_change', args=[next_p.pk])
            parts.append(format_html('<a href="{}">صفحه بعد (ص {})</a> →', url, next_p.page_number))
        else:
            parts.append(format_html('<span style="color:#ccc;">آخر کتاب →</span>'))
        return mark_safe('&ensp;|&ensp;'.join(parts))
    nav_links.short_description = 'ناوبری صفحه‌ها'

    # ── اکشن دسته‌جمعی ────────────────────────────────────────────────────
    actions = ['reorder_pages']

    @admin.action(description='مرتب‌سازی مجدد ترتیب صفحات بر اساس شماره صفحه')
    def reorder_pages(self, request, queryset):
        """
        برای هر کتاب منحصر به فرد در queryset،
        order را از ۱ مجدداً شماره‌گذاری می‌کند.
        """
        books_affected = set()
        for page in queryset.order_by('book', 'order'):
            books_affected.add(page.book_id)

        total = 0
        for book_id in books_affected:
            pages = BookPage.objects.filter(book_id=book_id).order_by('order')
            for i, p in enumerate(pages, start=1):
                if p.order != i:
                    p.order = i
                    p.save(update_fields=['order'])
                    total += 1

        self.message_user(request, f"ترتیب {total} صفحه در {len(books_affected)} کتاب به‌روز شد.")