from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from .models import PodcastCategory, PodcastSeries, Podcast


# ── دسته‌بندی پادکست ──────────────────────────────────────────────────────

@admin.register(PodcastCategory)
class PodcastCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'parent', 'icon', 'order', 'podcasts_count')
    list_editable = ('order',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_count=Count('podcasts'))

    def podcasts_count(self, obj):
        return obj._count
    podcasts_count.short_description = 'تعداد پادکست'
    podcasts_count.admin_order_field = '_count'


# ── Inline قسمت‌ها داخل مجموعه ───────────────────────────────────────────

class PodcastInline(admin.TabularInline):
    model  = Podcast
    extra  = 0
    fields = ('episode_number', 'title', 'host', 'access_type', 'price', 'duration', 'is_active')
    show_change_link = True
    ordering = ('episode_number',)


# ── مجموعه پادکست ─────────────────────────────────────────────────────────

@admin.register(PodcastSeries)
class PodcastSeriesAdmin(admin.ModelAdmin):
    list_display   = ('cover_thumbnail', 'title', 'host', 'category', 'episodes_count', 'is_featured', 'is_active')
    list_display_links = ('cover_thumbnail', 'title')
    list_editable  = ('is_featured', 'is_active')
    list_filter    = ('category', 'is_active', 'is_featured')
    search_fields  = ('title', 'host')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('cover_preview', 'created_at')
    inlines        = [PodcastInline]
    save_on_top    = True

    fieldsets = (
        ('اطلاعات مجموعه', {
            'fields': ('title', 'slug', 'host', 'category', 'description'),
        }),
        ('تصویر', {
            'fields': ('cover_image', 'cover_preview'),
        }),
        ('وضعیت', {
            'fields': ('is_active', 'is_featured', 'created_at'),
        }),
    )

    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:50%;"/>',
                obj.cover_image.url
            )
        return format_html('<div style="width:50px;height:50px;background:#f0f0f0;border-radius:50%;display:flex;align-items:center;justify-content:center;">🎙️</div>')
    cover_thumbnail.short_description = 'کاور'

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height:180px;border-radius:8px;"/>', obj.cover_image.url)
        return '—'
    cover_preview.short_description = 'پیش‌نمایش'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_episodes=Count('episodes'))

    def episodes_count(self, obj):
        return obj._episodes
    episodes_count.short_description = 'تعداد قسمت'
    episodes_count.admin_order_field = '_episodes'


# ── پادکست (قسمت) ─────────────────────────────────────────────────────────

class AccessTypeFilter(admin.SimpleListFilter):
    title = 'نوع دسترسی'
    parameter_name = 'access_type'

    def lookups(self, request, model_admin):
        return Podcast.AccessType.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(access_type=self.value())
        return queryset


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = (
        'cover_thumbnail', 'title', 'host', 'series', 'category',
        'episode_number', 'duration_display', 'access_badge',
        'price_display', 'plays', 'is_featured', 'is_active',
    )
    list_display_links = ('cover_thumbnail', 'title')
    list_editable      = ('is_featured', 'is_active')
    list_filter        = (AccessTypeFilter, 'series', 'category', 'is_active', 'is_featured')
    search_fields      = ('title', 'host', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields    = ('plays', 'downloads', 'created_at', 'updated_at', 'cover_preview', 'duration_readable')
    list_per_page      = 25
    date_hierarchy     = 'created_at'
    save_on_top        = True

    fieldsets = (
        ('اطلاعات قسمت', {
            'fields': ('title', 'slug', 'series', 'category', 'host', 'episode_number', 'description'),
        }),
        ('تصویر', {
            'fields': ('cover_image', 'cover_preview'),
            'classes': ('collapse',),
        }),
        ('فایل صوتی', {
            'fields': ('audio_file', 'audio_url', 'duration', 'duration_readable'),
        }),
        ('دسترسی و قیمت', {
            'fields': ('access_type', 'price', 'discount_percent'),
        }),
        ('وضعیت', {
            'fields': ('is_active', 'is_featured'),
        }),
        ('آمار', {
            'fields': ('plays', 'downloads', 'rating', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width:45px;height:45px;object-fit:cover;border-radius:6px;"/>',
                obj.cover_image.url
            )
        return '🎧'
    cover_thumbnail.short_description = 'کاور'

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height:180px;border-radius:8px;"/>', obj.cover_image.url)
        return '—'
    cover_preview.short_description = 'پیش‌نمایش'

    def duration_display(self, obj):
        return obj.duration_display
    duration_display.short_description = 'مدت زمان'

    def duration_readable(self, obj):
        return obj.duration_display
    duration_readable.short_description = 'مدت زمان (نمایش)'

    def access_badge(self, obj):
        colors = {'free': '#198754', 'paid': '#dc3545', 'premium': '#6f42c1'}
        color = colors.get(obj.access_type, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_access_type_display()
        )
    access_badge.short_description = 'دسترسی'

    def price_display(self, obj):
        if obj.access_type == 'free':
            return format_html('<span style="color:#198754;font-weight:bold;">رایگان</span>')
        return format_html('{:,} تومان', obj.final_price)
    price_display.short_description = 'قیمت'