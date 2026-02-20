from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from .models import CourseCategory, Course, CourseSection, CourseLesson


# ── دسته‌بندی دوره ─────────────────────────────────────────────────────────

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'parent', 'icon', 'order', 'courses_count')
    list_editable = ('order',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_count=Count('courses'))

    def courses_count(self, obj):
        return obj._count
    courses_count.short_description = 'تعداد دوره'
    courses_count.admin_order_field = '_count'


# ── Inline درس‌ها داخل بخش ───────────────────────────────────────────────

class CourseLessonInline(admin.TabularInline):
    model  = CourseLesson
    extra  = 1
    fields = ('order', 'title', 'lesson_type', 'duration', 'is_preview')
    ordering = ('order',)
    show_change_link = True


# ── Inline بخش‌ها داخل دوره ──────────────────────────────────────────────

class CourseSectionInline(admin.StackedInline):
    model  = CourseSection
    extra  = 0
    fields = ('order', 'title')
    ordering = ('order',)
    show_change_link = True


# ── دوره ویدیویی ──────────────────────────────────────────────────────────

class AccessTypeFilter(admin.SimpleListFilter):
    title = 'نوع دسترسی'
    parameter_name = 'access_type'

    def lookups(self, request, model_admin):
        return Course.AccessType.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(access_type=self.value())
        return queryset


class LevelFilter(admin.SimpleListFilter):
    title = 'سطح دوره'
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        return Course.Level.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(level=self.value())
        return queryset


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'cover_thumbnail', 'title', 'instructor', 'category',
        'level_badge', 'access_badge', 'price_display',
        'lessons_count', 'duration_display',
        'enrollments', 'rating', 'is_featured', 'is_active',
    )
    list_display_links = ('cover_thumbnail', 'title')
    list_editable      = ('is_featured', 'is_active')
    list_filter        = (AccessTypeFilter, LevelFilter, 'category', 'has_certificate', 'is_active', 'is_featured')
    search_fields      = ('title', 'instructor', 'short_desc')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields    = ('views', 'enrollments', 'created_at', 'updated_at', 'cover_preview')
    list_per_page      = 20
    date_hierarchy     = 'created_at'
    save_on_top        = True
    inlines            = [CourseSectionInline]

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'instructor', 'category', 'short_desc', 'description'),
        }),
        ('تصویر و ویدیو', {
            'fields': ('cover_image', 'cover_preview', 'intro_video_url'),
            'classes': ('collapse',),
        }),
        ('دسترسی و قیمت', {
            'fields': ('access_type', 'price', 'discount_percent'),
        }),
        ('مشخصات دوره', {
            'fields': ('level', 'total_duration', 'lessons_count', 'has_certificate'),
        }),
        ('وضعیت', {
            'fields': ('is_active', 'is_featured'),
        }),
        ('آمار', {
            'fields': ('views', 'enrollments', 'rating', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width:70px;height:45px;object-fit:cover;border-radius:6px;"/>',
                obj.cover_image.url
            )
        return format_html('<div style="width:70px;height:45px;background:#e9ecef;border-radius:6px;display:flex;align-items:center;justify-content:center;">🎬</div>')
    cover_thumbnail.short_description = 'کاور'

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height:200px;border-radius:8px;"/>', obj.cover_image.url)
        return '—'
    cover_preview.short_description = 'پیش‌نمایش'

    def level_badge(self, obj):
        colors = {
            'beginner':     '#198754',
            'intermediate': '#fd7e14',
            'advanced':     '#dc3545',
            'all':          '#0d6efd',
        }
        color = colors.get(obj.level, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_level_display()
        )
    level_badge.short_description = 'سطح'

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

    def duration_display(self, obj):
        return obj.duration_display
    duration_display.short_description = 'مدت کل'


# ── بخش دوره ─────────────────────────────────────────────────────────────

@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display  = ('title', 'course', 'order', 'lessons_count')
    list_editable = ('order',)
    list_filter   = ('course',)
    search_fields = ('title', 'course__title')
    ordering      = ('course', 'order')
    inlines       = [CourseLessonInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_lessons=Count('lessons'))

    def lessons_count(self, obj):
        return obj._lessons
    lessons_count.short_description = 'تعداد درس'
    lessons_count.admin_order_field = '_lessons'


# ── درس ──────────────────────────────────────────────────────────────────

@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display  = ('title', 'section', 'lesson_type_badge', 'duration_display', 'is_preview', 'order')
    list_editable = ('order', 'is_preview')
    list_filter   = ('lesson_type', 'is_preview', 'section__course')
    search_fields = ('title', 'section__title', 'section__course__title')
    ordering      = ('section', 'order')

    fieldsets = (
        ('اطلاعات درس', {
            'fields': ('section', 'title', 'lesson_type', 'order', 'is_preview'),
        }),
        ('محتوا', {
            'fields': ('video_url', 'video_file', 'duration'),
        }),
    )

    def lesson_type_badge(self, obj):
        icons = {
            'video': ('🎬', '#0d6efd'),
            'audio': ('🎧', '#fd7e14'),
            'pdf':   ('📄', '#dc3545'),
            'text':  ('📝', '#6c757d'),
            'quiz':  ('❓', '#198754'),
        }
        icon, color = icons.get(obj.lesson_type, ('📌', '#6c757d'))
        return format_html(
            '<span style="color:{};">{} {}</span>',
            color, icon, obj.get_lesson_type_display()
        )
    lesson_type_badge.short_description = 'نوع محتوا'

    def duration_display(self, obj):
        m, s = divmod(obj.duration, 60)
        return f"{m:02d}:{s:02d}"
    duration_display.short_description = 'مدت'