# Updated views.py with ajax views for dynamic filtering
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import SiteSettings, Slider, Banner, MenuItem, FAQ, GuideCategory,GuideArticle,SupportTicket
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


def support_home(request):
    """صفحه اصلی راهنما و پشتیبانی"""
    context = {
        'active_menu': 'support',
        'faqs': FAQ.objects.filter(is_active=True)[:6],
        'guide_categories': GuideCategory.objects.filter(is_active=True).order_by('order')[:4],
        'popular_articles': GuideArticle.objects.filter(is_active=True, is_popular=True)[:5],
        'support_email': 'support@mahboob.ir',
        'support_phone': '۰۲۱-۱۲۳۴۵۶۷۸',
        'support_hours': '۹ صبح تا ۹ شب (۷ روز هفته)',
    }
    return render(request, 'support/support.html', context)


def faq_list(request):
    """لیست سوالات متداول"""
    faqs = FAQ.objects.filter(is_active=True).order_by('order')
    
    # دسته‌بندی سوالات
    categories = FAQ.objects.values_list('category', flat=True).distinct()
    
    paginator = Paginator(faqs, 20)
    page = request.GET.get('page', 1)
    faqs_page = paginator.get_page(page)
    
    context = {
        'active_menu': 'support',
        'faqs': faqs_page,
        'categories': categories,
    }
    return render(request, 'main/support.html', context)


def guide_category(request, slug):
    """نمایش مقالات یک دسته راهنما"""
    category = get_object_or_404(GuideCategory, slug=slug, is_active=True)
    articles = GuideArticle.objects.filter(category=category, is_active=True).order_by('-created_at')
    
    context = {
        'active_menu': 'support',
        'category': category,
        'articles': articles,
    }
    return render(request, 'support/guide_category.html', context)


def guide_article(request, slug):
    """نمایش مقاله راهنما"""
    article = get_object_or_404(GuideArticle, slug=slug, is_active=True)
    
    # افزایش بازدید
    GuideArticle.objects.filter(pk=article.pk).update(views=article.views + 1)
    
    context = {
        'active_menu': 'support',
        'article': article,
    }
    return render(request, 'support/guide_article.html', context)




def create_ticket(request):
    """ایجاد تیکت پشتیبانی"""
    if request.method == 'POST':
        try:
            # دریافت داده‌ها از فرم
            fullname = request.POST.get('fullname', '').strip()
            email = request.POST.get('email', '').strip()
            category = request.POST.get('category', '').strip()
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()
            
            # اعتبارسنجی
            if not all([fullname, email, category, subject, message]):
                return render(request, 'main/support.html', {
                    'form_errors': 'لطفاً تمام فیلدها را پر کنید'
                })
            
            # ایجاد تیکت
            ticket = SupportTicket.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=email,
                fullname=fullname,
                category=category,
                subject=subject,
                message=message,
                status='pending'
            )
            
            messages.success(request, 'درخواست شما با موفقیت ثبت شد. به زودی پاسخگوی شما خواهیم بود.')
            return redirect('main:faq')
            
        except Exception as e:
            return render(request, 'main/support.html', {
                'form_errors': f'خطا در ثبت درخواست: {str(e)}'
            })
    
    return redirect('main:faq')


def contact_support(request):
    """تماس با پشتیبانی"""
    context = {
        'active_menu': 'support',
        'support_email': 'support@mahboob.ir',
        'support_phone': '۰۲۱-۱۲۳۴۵۶۷۸',
        'support_telegram': '@mahboob_support',
        'support_instagram': '@mahboob_app',
        'support_hours': '۹ صبح تا ۹ شب',
        'response_time': '۲۴ ساعت',
    }
    return render(request, 'support/contact.html', context)