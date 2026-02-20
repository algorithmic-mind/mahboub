# book/urls.py
from django.urls import path, re_path
from . import views

app_name = 'books'

urlpatterns = [
    path('',                            views.books_list,        name='books_list'),
    path('partial/',                    views.books_partial,     name='books_partial'),
    # <slug:slug> فقط ASCII قبول می‌کند — از re_path با unicode استفاده می‌کنیم
    re_path(r'category/(?P<slug>[^/]+)/', views.books_by_category, name='books_by_category'),
    re_path(r'(?P<slug>[^/]+)/',          views.book_detail,       name='book_detail'),
]