"""
book/views.py — اضافه شدن book_reader به views قبلی
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Book, BookCategory, BookPage, BookChapter

PAGE_SIZE = 12

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

ICONS = [
    "quran", "book-quran", "mosque", "book-reader",
    "book", "scroll", "feather", "book-open",
    "dove", "star-and-crescent", "hands-praying", "crown",
]


def _enrich_books(queryset):
    books = list(queryset)
    for book in books:
        idx = book.pk % len(GRADIENTS)
        book.gradient = GRADIENTS[idx]
        book.cover_icon = ICONS[idx % len(ICONS)]
    return books


def books_list(request):
    categories = BookCategory.objects.filter(
        parent__isnull=True
    ).prefetch_related('books').order_by('order', 'name')

    grouped = {}
    for cat in categories:
        books = _enrich_books(
            Book.objects.filter(is_active=True, category=cat)
            .select_related('category')
            .order_by('-created_at')[:6]
        )
        if books:
            grouped[cat] = books

    context = {
        'grouped_books': grouped,
        'active_menu': 'books',
    }
    return render(request, 'books/books.html', context)


def books_by_category(request, slug):
    category = get_object_or_404(BookCategory, slug=slug)

    qs = Book.objects.filter(
        is_active=True, category=category
    ).select_related('category')

    q      = request.GET.get('q', '').strip()
    access = request.GET.get('access', '').strip()
    sort   = request.GET.get('sort', '-created_at').strip()

    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(author__icontains=q)
        qs = qs.distinct()
    if access in ('free', 'paid', 'premium'):
        qs = qs.filter(access_type=access)

    ALLOWED = ('-created_at', '-views', '-rating', 'price', '-price')
    if sort not in ALLOWED:
        sort = '-created_at'
    qs = qs.order_by(sort)

    paginator  = Paginator(qs, PAGE_SIZE)
    page_obj   = paginator.get_page(request.GET.get('page', 1))
    books      = _enrich_books(page_obj.object_list)
    page_obj.enriched = books

    context = {
        'category':        category,
        'page_obj':        page_obj,
        'books':           books,
        'search_query':    q,
        'selected_access': access,
        'selected_sort':   sort,
        'active_menu':     'books',
    }
    return render(request, 'books/books_category.html', context)


def book_detail(request, slug):
    book     = get_object_or_404(Book, slug=slug, is_active=True)
    chapters = book.chapters.prefetch_related('pages').order_by('order')

    Book.objects.filter(pk=book.pk).update(views=book.views + 1)

    idx = book.pk % len(GRADIENTS)
    book.gradient  = GRADIENTS[idx]
    book.cover_icon = ICONS[idx % len(ICONS)]

    # بررسی دسترسی
    from purchase.models import Purchase
    has_access = (
        book.access_type == 'free'
        or Purchase.has_access(request.user, 'book', book.pk)
    )

    context = {
        'book':        book,
        'chapters':    chapters,
        'has_access':  has_access,
        'active_menu': 'books',
    }
    return render(request, 'books/book_detail.html', context)


# ─────────────────────────────────────────────────────────────────────────
# Book Reader — بر اساس دیتابیس BookPage
# ─────────────────────────────────────────────────────────────────────────

from django.contrib.auth.decorators import login_required

@login_required(login_url='/account/login/')
def book_reader(request, slug):
    """صفحه خواندن — نیاز به لاگین — از دیتابیس BookPage"""
    book = get_object_or_404(Book, slug=slug, is_active=True)

    from purchase.models import Purchase
    # فقط فصل‌های preview یا خریداری‌شده
    has_access = (
        book.access_type == 'free'
        or Purchase.has_access(request.user, 'book', book.pk)
    )

    # صفحه درخواستی
    try:
        page_order = int(request.GET.get('page', 1))
    except ValueError:
        page_order = 1

    # صفحه‌های قابل‌دسترس
    if has_access:
        pages_qs = BookPage.objects.filter(book=book).order_by('order')
    else:
        # فقط صفحات فصل‌های preview
        preview_chapters = book.chapters.filter(is_preview=True)
        if preview_chapters.exists():
            pages_qs = BookPage.objects.filter(
                book=book, chapter__in=preview_chapters
            ).order_by('order')
        else:
            # اگر هیچ فصل preview‌ای نیست، ۵ صفحه اول نشان بده
            pages_qs = BookPage.objects.filter(book=book).order_by('order')[:5]

    total_pages = pages_qs.count()
    if total_pages == 0:
        # محتوایی در دیتابیس نیست — نمایش نمونه استاتیک
        return render(request, 'books/book_reader.html', {
            'book': book,
            'page': None,
            'total_pages': 0,
            'has_access': has_access,
            'no_content': True,
        })

    page_order = max(1, min(page_order, total_pages))
    page_list  = list(pages_qs)
    current_page = page_list[page_order - 1]

    context = {
        'book':         book,
        'page':         current_page,
        'page_order':   page_order,
        'total_pages':  total_pages,
        'has_prev':     page_order > 1,
        'has_next':     page_order < total_pages,
        'has_access':   has_access,
        'no_content':   False,
    }
    return render(request, 'books/book_reader.html', context)


def book_page_api(request, slug):
    """AJAX — بارگذاری یک صفحه بدون reload"""
    book = get_object_or_404(Book, slug=slug, is_active=True)
    try:
        page_order = int(request.GET.get('page', 1))
    except ValueError:
        return JsonResponse({'error': 'invalid'}, status=400)

    from purchase.models import Purchase
    has_access = (
        book.access_type == 'free'
        or Purchase.has_access(request.user, 'book', book.pk)
    )

    if has_access:
        page = BookPage.objects.filter(book=book, order=page_order).first()
    else:
        preview_chapters = book.chapters.filter(is_preview=True)
        page = BookPage.objects.filter(
            book=book, order=page_order, chapter__in=preview_chapters
        ).first()

    if not page:
        return JsonResponse({'error': 'not_found'}, status=404)

    return JsonResponse({
        'page_number': page.page_number,
        'heading':     page.heading,
        'content':     page.content,
        'order':       page.order,
    })