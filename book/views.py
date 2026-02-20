# book/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Book, BookCategory

BOOKS_PER_CATEGORY = 6
PAGE_SIZE = 12


def _apply_filters(request):
    """پارامترهای GET را پردازش کرده و queryset فیلتر شده برمی‌گرداند."""
    qs = Book.objects.filter(is_active=True).select_related('category')

    q      = request.GET.get('q', '').strip()
    cat    = request.GET.get('cat', '').strip()
    access = request.GET.get('access', '').strip()
    sort   = request.GET.get('sort', '-created_at').strip()

    if q:
        qs = (
            Book.objects.filter(is_active=True, title__icontains=q).select_related('category') |
            Book.objects.filter(is_active=True, author__icontains=q).select_related('category')
        ).distinct()
    if cat:
        qs = qs.filter(category__slug=cat)
    if access in ('free', 'paid', 'premium'):
        qs = qs.filter(access_type=access)

    ALLOWED_SORTS = ('-created_at', '-views', '-rating', 'price', '-price')
    if sort not in ALLOWED_SORTS:
        sort = '-created_at'
    qs = qs.order_by(sort)

    return qs, q, cat, access, sort


def _build_context(request, qs, q, selected_cat, selected_access, selected_sort, categories):
    """grouped یا flat context بر اساس وضعیت فیلتر."""
    is_filtered = q or selected_cat or selected_access or selected_sort != '-created_at'

    if not is_filtered:
        grouped_books = {}
        for cat in categories:
            books = list(qs.filter(category=cat)[:BOOKS_PER_CATEGORY])
            if books:
                grouped_books[cat] = books
        return {'grouped_books': grouped_books, 'flat_books': None}
    else:
        paginator  = Paginator(qs, PAGE_SIZE)
        flat_books = paginator.get_page(request.GET.get('page', 1))
        return {'grouped_books': None, 'flat_books': flat_books}


def books_list(request):
    """صفحه اصلی کتابخانه."""
    categories = BookCategory.objects.filter(parent__isnull=True).order_by('order', 'name')
    qs, q, selected_cat, selected_access, selected_sort = _apply_filters(request)
    ctx = _build_context(request, qs, q, selected_cat, selected_access, selected_sort, categories)

    context = {
        'categories':      categories,
        'selected_cat':    selected_cat,
        'selected_access': selected_access,
        'selected_sort':   selected_sort,
        'search_query':    q,
        'active_menu':     'books',
        **ctx,
    }
    return render(request, 'books/books.html', context)


def books_partial(request):
    """HTMX endpoint — فقط partial برمی‌گرداند."""
    categories = BookCategory.objects.filter(parent__isnull=True).order_by('order', 'name')
    qs, q, selected_cat, selected_access, selected_sort = _apply_filters(request)
    ctx = _build_context(request, qs, q, selected_cat, selected_access, selected_sort, categories)

    return render(request, 'book/partials/books_list.html', {
        **ctx,
        'selected_sort': selected_sort,
    })


def books_by_category(request, slug):
    """صفحه 'مشاهده همه' یک دسته."""
    category   = get_object_or_404(BookCategory, slug=slug)
    categories = BookCategory.objects.filter(parent__isnull=True).order_by('order', 'name')

    qs, q, selected_cat, selected_access, selected_sort = _apply_filters(request)
    qs = qs.filter(category=category)

    paginator  = Paginator(qs, PAGE_SIZE)
    flat_books = paginator.get_page(request.GET.get('page', 1))

    context = {
        'categories':       categories,
        'grouped_books':    None,
        'flat_books':       flat_books,
        'current_category': category,
        'selected_cat':     slug,
        'selected_access':  selected_access,
        'selected_sort':    selected_sort,
        'search_query':     q,
        'active_menu':      'books',
    }
    return render(request, 'book/books.html', context)


def book_detail(request, slug):
    """صفحه جزئیات کتاب."""
    book     = get_object_or_404(Book, slug=slug, is_active=True)
    chapters = book.chapters.prefetch_related('pages').order_by('order')

    # ثبت بازدید بدون race condition
    Book.objects.filter(pk=book.pk).update(views=book.views + 1)

    context = {
        'book':        book,
        'chapters':    chapters,
        'active_menu': 'books',
    }
    return render(request, 'book/book_detail.html', context)