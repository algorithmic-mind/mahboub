# books/admin.py
from django.contrib import admin
from django.utils.html import format_html, mark_safe, mark_safe
from django.db.models import Count
from .models import BookCategory, Book, BookChapter, BookPage


# ══════════════════════════════════════════════════════════════════════════
#  BookCategory
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
            return format_html('<i class="{}"></i> <small>{}</small>', obj.icon, obj.icon)
        return '—'
    icon_preview.short_description = 'آیکون'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _books_count=Count('books')
        )

    def books_count(self, obj):
        return obj._books_count
    books_count.short_description = 'تعداد کتاب'
    books_count.admin_order_field = '_books_count'


# ══════════════════════════════════════════════════════════════════════════
#  Inlines
# ══════════════════════════════════════════════════════════════════════════

class BookPageInline(admin.TabularInline):
    model          = BookPage
    extra          = 0
    fields         = ('order', 'page_number', 'chapter', 'heading', 'content')
    ordering       = ('order',)
    show_change_link = True

    def get_queryset(self, request):
        # برای جلوگیری از کندی، فقط ۵ صفحه اول نمایش داده می‌شود
        return super().get_queryset(request)[:5]


class BookChapterInline(admin.TabularInline):
    model  = BookChapter
    extra  = 1
    fields = ('order', 'title', 'is_preview')
    ordering = ('order',)
    show_change_link = True


# ══════════════════════════════════════════════════════════════════════════
#  Book
# ══════════════════════════════════════════════════════════════════════════

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'cover_thumbnail', 'title', 'author', 'category',
        'access_badge', 'price_display', 'rating',
        'views', 'is_featured', 'is_active',
    )
    list_display_links = ('cover_thumbnail', 'title')
    list_filter  = ('is_active', 'is_featured', 'access_type', 'category', 'language')
    list_editable = ('is_featured', 'is_active')
    search_fields = ('title', 'author', 'translator', 'publisher', 'isbn')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'rating', 'created_at', 'updated_at', 'cover_preview', 'final_price_display')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [BookChapterInline]

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                'title', 'slug', 'author', 'translator',
                'publisher', 'description',
            )
        }),
        ('تصویر جلد', {
            'fields': ('cover_image', 'cover_preview'),
        }),
        ('دسته‌بندی و دسترسی', {
            'fields': (
                'category',
                'access_type', 'price', 'discount_percent', 'final_price_display',
            )
        }),
        ('مشخصات کتاب', {
            'fields': ('volume', 'isbn', 'language', 'publish_year'),
            'classes': ('collapse',),
        }),
        ('وضعیت', {
            'fields': ('is_active', 'is_featured'),
        }),
        ('آمار (فقط خواندن)', {
            'fields': ('views', 'rating', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # ── نمایش‌های سفارشی ──────────────────────────────────────────────────

    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:48px;width:36px;object-fit:cover;border-radius:4px;">',
                obj.cover_image.url
            )
        return mark_safe(
            '<div style="height:48px;width:36px;background:#eee;border-radius:4px;'
            'display:flex;align-items:center;justify-content:center;font-size:18px;">📖</div>'
        )
    cover_thumbnail.short_description = ''

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:8px;">',
                obj.cover_image.url
            )
        return '—'
    cover_preview.short_description = 'پیش‌نمایش جلد'

    def access_badge(self, obj):
        colors = {
            'free':    ('#2e7d32', '#e8f5e9', 'رایگان'),
            'paid':    ('#1565c0', '#e3f2fd', 'پولی'),
            'premium': ('#6a1b9a', '#f3e5f5', 'ویژه'),
        }
        color, bg, label = colors.get(obj.access_type, ('#555', '#eee', obj.access_type))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;'
            'border-radius:12px;font-size:11px;font-weight:bold;">{}</span>',
            bg, color, label
        )
    access_badge.short_description = 'دسترسی'

    def price_display(self, obj):
        if obj.access_type == 'free':
            return mark_safe('<span style="color:#2e7d32;">رایگان</span>')
        if obj.discount_percent:
            return format_html(
                '<span style="text-decoration:line-through;color:#999;font-size:11px;">{:,}</span>'
                ' <strong style="color:#d32f2f;">{:,}</strong> <small>ت</small>',
                obj.price, obj.final_price
            )
        return format_html('{:,} <small>ت</small>', obj.price)
    price_display.short_description = 'قیمت'

    def final_price_display(self, obj):
        return f'{obj.final_price:,} تومان'
    final_price_display.short_description = 'قیمت نهایی (با تخفیف)'


# ══════════════════════════════════════════════════════════════════════════
#  BookChapter
# ══════════════════════════════════════════════════════════════════════════

@admin.register(BookChapter)
class BookChapterAdmin(admin.ModelAdmin):
    list_display  = ('title', 'book', 'order', 'is_preview', 'pages_count')
    list_filter   = ('is_preview', 'book')
    search_fields = ('title', 'book__title')
    list_editable = ('order', 'is_preview')
    ordering      = ('book', 'order')
    autocomplete_fields = ('book',)

    def pages_count(self, obj):
        return obj.pages.count()
    pages_count.short_description = 'تعداد صفحات'


# ══════════════════════════════════════════════════════════════════════════
#  BookPage
# ══════════════════════════════════════════════════════════════════════════

@admin.register(BookPage)
class BookPageAdmin(admin.ModelAdmin):
    list_display  = ('book', 'chapter', 'order', 'page_number', 'heading_short', 'content_preview')
    list_filter   = ('book', 'chapter')
    search_fields = ('book__title', 'heading', 'content', 'page_number')
    list_editable = ('order', 'page_number')
    ordering      = ('book', 'order')
    autocomplete_fields = ('book', 'chapter')
    readonly_fields = ('page_image_preview',)

    fieldsets = (
        ('موقعیت', {
            'fields': ('book', 'chapter', 'order', 'page_number'),
        }),
        ('محتوا', {
            'fields': ('heading', 'content'),
        }),
        ('تصویر صفحه', {
            'fields': ('page_image', 'page_image_preview'),
            'classes': ('collapse',),
        }),
        ('یادداشت داخلی', {
            'fields': ('editor_note',),
            'classes': ('collapse',),
        }),
    )

    def heading_short(self, obj):
        return obj.heading[:40] + '…' if len(obj.heading) > 40 else obj.heading or '—'
    heading_short.short_description = 'عنوان میانی'

    def content_preview(self, obj):
        return obj.content[:60] + '…' if len(obj.content) > 60 else obj.content
    content_preview.short_description = 'پیش‌نمایش متن'

    def page_image_preview(self, obj):
        if obj.page_image:
            return format_html(
                '<img src="{}" style="max-height:180px;border-radius:6px;">',
                obj.page_image.url
            )
        return '—'
    page_image_preview.short_description = 'پیش‌نمایش تصویر'