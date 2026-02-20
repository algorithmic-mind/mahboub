# Updated views.py with ajax views for dynamic filtering
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from .models import SiteSettings, Slider, Banner, MenuItem
from book.models import Book, BookCategory  # Assuming books app
from podcast.models import Podcast, PodcastCategory  # Assuming podcasts app
from course.models import Course, CourseCategory  # Assuming courses app

def main(request):
    settings = SiteSettings.get()

    # اسلایدر صفحه اصلی — بالا
    try:
        slider = Slider.objects.filter(
            position=Slider.SliderPosition.HOME_TOP,
            is_active=True
        ).prefetch_related('slides').first()
        slides = slider.slides.filter(is_active=True) if slider else []
    except Exception:
        slider, slides = None, []

    # بنر میانی صفحه اصلی
    now = timezone.now()
    banners = Banner.objects.filter(
        position=Banner.BannerPosition.HOME_BOTTOM,
        is_active=True,
    ).filter(
        Q(starts_at__isnull=True) | Q(starts_at__lte=now),
        Q(ends_at__isnull=True)   | Q(ends_at__gte=now),
    )

    # منوی هدر
    header_menu = MenuItem.objects.filter(
        location=MenuItem.MenuLocation.HEADER,
        is_active=True,
        parent__isnull=True,
    ).prefetch_related('children')

    # منوی فوتر
    footer_menu = MenuItem.objects.filter(
        location=MenuItem.MenuLocation.FOOTER,
        is_active=True,
    )

    # منوی نوار پایین موبایل
    bottom_menu = MenuItem.objects.filter(
        location=MenuItem.MenuLocation.BOTTOM,
        is_active=True,
    )

    # Fetch categories for dynamic tabs
    book_categories = BookCategory.objects.filter(parent__isnull=True).order_by('order')[:5]  # Limit to 5 for tabs
    podcast_categories = PodcastCategory.objects.filter(parent__isnull=True).order_by('order')[:5]
    course_categories = CourseCategory.objects.filter(parent__isnull=True).order_by('order')[:5]

    # Fetch initial featured content
    featured_books = Book.objects.filter(is_featured=True, is_active=True)[:10]
    featured_podcasts = Podcast.objects.filter(is_featured=True, is_active=True)[:10]
    featured_courses = Course.objects.filter(is_featured=True, is_active=True)[:10]

    context = {
        'site_settings': settings,
        'slider': slider,
        'slides': slides,
        'banners': banners,
        'header_menu': header_menu,
        'footer_menu': footer_menu,
        'bottom_menu': bottom_menu,
        'active_menu': 'home',
        'book_categories': book_categories,
        'podcast_categories': podcast_categories,
        'course_categories': course_categories,
        'featured_books': featured_books,
        'featured_podcasts': featured_podcasts,
        'featured_courses': featured_courses,
    }
    return render(request, 'main/index.html', context)

# AJAX views for dynamic filtering
from django.shortcuts import get_object_or_404

def ajax_books(request):
    category_slug = request.GET.get('category', 'all')
    if category_slug == 'all':
        books = Book.objects.filter(is_featured=True, is_active=True)[:10]
    else:
        category = get_object_or_404(BookCategory, slug=category_slug)
        books = Book.objects.filter(category=category, is_featured=True, is_active=True)[:10]
    return render(request, 'main/partials/books_row.html', {'featured_books': books})

def ajax_podcasts(request):
    category_slug = request.GET.get('category', 'all')
    if category_slug == 'all':
        podcasts = Podcast.objects.filter(is_featured=True, is_active=True)[:10]
    else:
        category = get_object_or_404(PodcastCategory, slug=category_slug)
        podcasts = Podcast.objects.filter(category=category, is_featured=True, is_active=True)[:10]
    return render(request, 'main/partials/podcasts_row.html', {'featured_podcasts': podcasts})

def ajax_courses(request):
    category_slug = request.GET.get('category', 'all')
    if category_slug == 'all':
        courses = Course.objects.filter(is_featured=True, is_active=True)[:10]
    else:
        category = get_object_or_404(CourseCategory, slug=category_slug)
        courses = Course.objects.filter(category=category, is_featured=True, is_active=True)[:10]
    return render(request, 'main/partials/courses_row.html', {'featured_courses': courses})