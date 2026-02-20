from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, Slider, SliderSlide, Banner, MenuItem


# ── اسلاید داخل اسلایدر (Inline) ─────────────────────────────────────────

class SliderSlideInline(admin.StackedInline):
    model   = SliderSlide
    extra   = 1
    fields  = ('order', 'image', 'slide_preview', 'mobile_image', 'title', 'subtitle', 'link', 'link_text', 'is_active')
    readonly_fields = ('slide_preview',)
    ordering = ('order',)

    def slide_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:120px;object-fit:cover;border-radius:6px;"/>',
                obj.image.url
            )
        return '—'
    slide_preview.short_description = 'پیش‌نمایش تصویر'


# ── اسلایدر ──────────────────────────────────────────────────────────────

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display  = ('title', 'position_badge', 'slides_count', 'auto_play', 'interval', 'is_active')
    list_editable = ('auto_play', 'interval', 'is_active')
    list_filter   = ('position', 'is_active')
    inlines       = [SliderSlideInline]
    save_on_top   = True

    fieldsets = (
        ('اطلاعات اسلایدر', {
            'fields': ('title', 'position', 'is_active'),
        }),
        ('تنظیمات پخش', {
            'fields': ('auto_play', 'interval'),
        }),
    )

    def position_badge(self, obj):
        colors = {
            'home_top':    '#0d6efd',
            'home_middle': '#6f42c1',
            'books':       '#198754',
            'courses':     '#fd7e14',
        }
        color = colors.get(obj.position, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_position_display()
        )
    position_badge.short_description = 'محل نمایش'

    def get_queryset(self, request):
        from django.db.models import Count
        return super().get_queryset(request).annotate(_slides=Count('slides'))

    def slides_count(self, obj):
        return obj._slides
    slides_count.short_description = 'تعداد اسلاید'


# ── بنر ──────────────────────────────────────────────────────────────────

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display  = ('banner_preview', 'title', 'position_badge', 'order', 'starts_at', 'ends_at', 'is_active')
    list_display_links = ('banner_preview', 'title')
    list_editable = ('order', 'is_active')
    list_filter   = ('position', 'is_active')
    search_fields = ('title',)

    fieldsets = (
        ('اطلاعات بنر', {
            'fields': ('title', 'image', 'banner_preview_field', 'link', 'position', 'order'),
        }),
        ('زمان‌بندی نمایش', {
            'fields': ('starts_at', 'ends_at', 'is_active'),
        }),
    )
    readonly_fields = ('banner_preview_field',)

    def banner_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:120px;max-height:50px;object-fit:cover;border-radius:4px;"/>',
                obj.image.url
            )
        return '—'
    banner_preview.short_description = 'پیش‌نمایش'

    def banner_preview_field(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:400px;border-radius:8px;"/>',
                obj.image.url
            )
        return '—'
    banner_preview_field.short_description = 'پیش‌نمایش بنر'

    def position_badge(self, obj):
        colors = {
            'sidebar':     '#6c757d',
            'home_bottom': '#0d6efd',
            'in_content':  '#fd7e14',
            'popup':       '#dc3545',
        }
        color = colors.get(obj.position, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_position_display()
        )
    position_badge.short_description = 'موقعیت'


# ── منو ───────────────────────────────────────────────────────────────────

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display  = ('label', 'location_badge', 'parent', 'url', 'icon_preview', 'order', 'open_new_tab', 'is_active')
    list_editable = ('order', 'is_active', 'open_new_tab')
    list_filter   = ('location', 'is_active')
    search_fields = ('label', 'url')
    ordering      = ('location', 'order')

    fieldsets = (
        ('اطلاعات آیتم', {
            'fields': ('label', 'url', 'icon', 'location', 'parent', 'order'),
        }),
        ('تنظیمات', {
            'fields': ('is_active', 'open_new_tab'),
        }),
    )

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{}" style="font-size:16px;"></i> <small>{}</small>', obj.icon, obj.icon)
        return '—'
    icon_preview.short_description = 'آیکون'

    def location_badge(self, obj):
        colors = {
            'header': '#0d6efd',
            'footer': '#6c757d',
            'bottom': '#198754',
        }
        color = colors.get(obj.location, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_location_display()
        )
    location_badge.short_description = 'محل'


# ── تنظیمات سایت (Singleton) ─────────────────────────────────────────────

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    save_on_top = True

    def has_add_permission(self, request):
        """فقط یک رکورد مجاز است"""
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = (
        'updated_at',
        'logo_preview', 'logo_dark_preview', 'favicon_preview',
    )

    fieldsets = (
        ('🏷️  هویت سایت', {
            'fields': ('site_name', 'site_description'),
        }),
        ('🖼️  لوگو و آیکون', {
            'fields': (
                ('logo', 'logo_preview'),
                ('logo_dark', 'logo_dark_preview'),
                ('favicon', 'favicon_preview'),
            ),
        }),
        ('🎨  قالب و فونت', {
            'fields': ('font_primary', 'font_custom_url', 'color_primary', 'color_secondary', 'color_accent'),
        }),
        ('📞  اطلاعات تماس', {
            'fields': ('email', 'phone', 'address'),
            'classes': ('collapse',),
        }),
        ('🔗  شبکه‌های اجتماعی', {
            'fields': ('telegram', 'instagram', 'whatsapp','bale','eitaa'),
            'classes': ('collapse',),
        }),
        ('🔍  SEO و ردیابی', {
            'fields': ('meta_keywords', 'google_analytics_id'),
            'classes': ('collapse',),
        }),
        ('💻  اسکریپت‌های سفارشی', {
            'fields': ('head_scripts', 'footer_scripts'),
            'classes': ('collapse',),
            'description': 'اسکریپت‌ها مستقیماً در HTML درج می‌شوند — با احتیاط وارد کنید.',
        }),
        ('⚙️  تنظیمات عمومی', {
            'fields': ('maintenance_mode', 'maintenance_message', 'ai_welcome_popup', 'footer_text', 'copyright_text'),
        }),
        ('📅  تاریخچه', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )

    # ── پیش‌نمایش تصاویر ─────────────────────────────────────────────────
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height:60px;background:#f8f9fa;padding:6px;border-radius:6px;"/>',
                obj.logo.url
            )
        return '(لوگو آپلود نشده)'
    logo_preview.short_description = 'پیش‌نمایش لوگو'

    def logo_dark_preview(self, obj):
        if obj.logo_dark:
            return format_html(
                '<img src="{}" style="max-height:60px;background:#212529;padding:6px;border-radius:6px;"/>',
                obj.logo_dark.url
            )
        return '(لوگو تاریک آپلود نشده)'
    logo_dark_preview.short_description = 'پیش‌نمایش لوگو (تاریک)'

    def favicon_preview(self, obj):
        if obj.favicon:
            return format_html(
                '<img src="{}" style="width:32px;height:32px;border-radius:4px;"/>',
                obj.favicon.url
            )
        return '(فاویکون آپلود نشده)'
    favicon_preview.short_description = 'پیش‌نمایش فاویکون'

    def changelist_view(self, request, extra_context=None):
        """ریدایرکت مستقیم به صفحه ویرایش تنها رکورد"""
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(
            reverse('admin:main_sitesettings_change', args=[obj.pk])
        )