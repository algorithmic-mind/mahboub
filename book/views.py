# book/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Book, BookCategory

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
    """gradient و icon را به هر کتاب اضافه می‌کند — بدون templatetag."""
    books = list(queryset)
    for book in books:
        idx = book.pk % len(GRADIENTS)
        book.gradient = GRADIENTS[idx]
        book.cover_icon = ICONS[idx % len(ICONS)]
    return books


def books_list(request):
    """صفحه اصلی کتابخانه — گروه‌بندی بر اساس دسته‌بندی."""
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
    """صفحه اختصاصی یک دسته‌بندی با pagination و فیلتر."""
    category = get_object_or_404(BookCategory, slug=slug)

    qs = Book.objects.filter(
        is_active=True, category=category
    ).select_related('category')

    # فیلترها
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
    page_obj.enriched = books  # attach برای دسترسی در template

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
    """صفحه جزئیات کتاب."""
    book     = get_object_or_404(Book, slug=slug, is_active=True)
    chapters = book.chapters.prefetch_related('pages').order_by('order')

    Book.objects.filter(pk=book.pk).update(views=book.views + 1)

    # gradient برای جلد
    idx = book.pk % len(GRADIENTS)
    book.gradient  = GRADIENTS[idx]
    book.cover_icon = ICONS[idx % len(ICONS)]

    context = {
        'book':        book,
        'chapters':    chapters,
        'active_menu': 'books',
    }
    return render(request, 'books/book_detail.html', context)