# book/urls.py
from django.urls import re_path
from . import views

app_name = 'books'

urlpatterns = [
    re_path(r'^$',                               views.books_list,        name='books_list'),
    re_path(r'^category/(?P<slug>[^/]+)/$',      views.books_by_category, name='books_by_category'),
    re_path(r'^(?P<slug>[^/]+)/$',               views.book_detail,       name='book_detail'),
]