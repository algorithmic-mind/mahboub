"""course/views.py"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Course, CourseCategory, CourseSection, CourseLesson

GRADIENTS = [
    "linear-gradient(135deg,#667eea,#764ba2)",
    "linear-gradient(135deg,#f093fb,#f5576c)",
    "linear-gradient(135deg,#4facfe,#00f2fe)",
    "linear-gradient(135deg,#fa709a,#fee140)",
    "linear-gradient(135deg,#a8edea,#fed6e3)",
    "linear-gradient(135deg,#ff9a9e,#fecfef)",
    "linear-gradient(135deg,#ffecd2,#fcb69f)",
    "linear-gradient(135deg,#a1c4fd,#c2e9fb)",
    "linear-gradient(135deg,#d299c2,#fef9d7)",
    "linear-gradient(135deg,#f6d365,#fda085)",
    "linear-gradient(135deg,#84fab0,#8fd3f4)",
    "linear-gradient(135deg,#96deda,#50c9c3)",
]
ICONS = ["video","play-circle","film","chalkboard-teacher","graduation-cap","book-reader","mosque","scroll","dove","star-and-crescent","hands-praying","crown"]


def _enrich(qs):
    items = list(qs)
    for c in items:
        idx = c.pk % len(GRADIENTS)
        c.gradient  = GRADIENTS[idx]
        c.cover_icon= ICONS[idx % len(ICONS)]
    return items


def courses_list(request):
    categories = CourseCategory.objects.filter(parent__isnull=True).order_by('order')
    grouped = {}
    for cat in categories:
        courses = _enrich(
            Course.objects.filter(is_active=True, category=cat)
            .select_related('category')
            .order_by('-created_at')[:6]
        )
        if courses:
            grouped[cat] = courses

    featured = Course.objects.filter(is_active=True, is_featured=True).first()
    if featured:
        idx = featured.pk % len(GRADIENTS)
        featured.gradient   = GRADIENTS[idx]
        featured.cover_icon = ICONS[idx % len(ICONS)]

    return render(request, 'courses/courses.html', {
        'grouped_courses': grouped,
        'featured':        featured,
        'active_menu':     'courses',
    })


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    Course.objects.filter(pk=course.pk).update(views=course.views + 1)

    idx = course.pk % len(GRADIENTS)
    course.gradient   = GRADIENTS[idx]
    course.cover_icon = ICONS[idx % len(ICONS)]

    sections = course.sections.prefetch_related('lessons').order_by('order')

    from purchase.models import Purchase
    has_access = (
        course.access_type == 'free'
        or Purchase.has_access(request.user, 'course', course.pk)
    )

    # اولین درس رایگان (preview)
    first_lesson = None
    for section in sections:
        for lesson in section.lessons.order_by('order'):
            if lesson.is_preview or has_access:
                first_lesson = lesson
                break
        if first_lesson:
            break

    return render(request, 'courses/course_detail.html', {
        'course':       course,
        'sections':     sections,
        'has_access':   has_access,
        'first_lesson': first_lesson,
        'active_menu':  'courses',
    })


def lesson_view(request, course_slug, lesson_id):
    """نمایش درس (ویدیو/محتوا)"""
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    lesson = get_object_or_404(CourseLesson, pk=lesson_id, section__course=course)

    from purchase.models import Purchase
    has_access = (
        lesson.is_preview
        or course.access_type == 'free'
        or Purchase.has_access(request.user, 'course', course.pk)
    )

    if not has_access:
        return render(request, 'courses/lesson_locked.html', {
            'course': course,
            'lesson': lesson,
        })

    idx = course.pk % len(GRADIENTS)
    course.gradient = GRADIENTS[idx]

    sections = course.sections.prefetch_related('lessons').order_by('order')

    return render(request, 'courses/lesson_view.html', {
        'course':   course,
        'lesson':   lesson,
        'sections': sections,
        'active_menu': 'courses',
    })


def courses_by_category(request, slug):
    category = get_object_or_404(CourseCategory, slug=slug)
    qs = Course.objects.filter(is_active=True, category=category).select_related('category')

    q      = request.GET.get('q', '').strip()
    access = request.GET.get('access', '')
    level  = request.GET.get('level', '')
    sort   = request.GET.get('sort', '-created_at')

    if q:
        qs = (qs.filter(title__icontains=q) | qs.filter(instructor__icontains=q)).distinct()
    if access in ('free','paid','premium'):
        qs = qs.filter(access_type=access)
    if level in ('beginner','intermediate','advanced','all'):
        qs = qs.filter(level=level)
    if sort not in ('-created_at','-enrollments','-rating','price','-price'):
        sort = '-created_at'
    qs = qs.order_by(sort)

    paginator = Paginator(qs, 12)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    courses   = _enrich(page_obj.object_list)

    return render(request, 'courses/courses_category.html', {
        'category':        category,
        'page_obj':        page_obj,
        'courses':         courses,
        'search_query':    q,
        'selected_access': access,
        'selected_level':  level,
        'selected_sort':   sort,
        'active_menu':     'courses',
    })