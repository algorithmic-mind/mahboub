# Add to urls.py in main app
from django.urls import path
from .views import main, ajax_books, ajax_podcasts, ajax_courses, faq_list,guide_article,guide_category,create_ticket,contact_support

app_name = 'main'
urlpatterns = [
    path('', main, name='main'),
    path('ajax-books/', ajax_books, name='ajax_books'),
    path('ajax-podcasts/', ajax_podcasts, name='ajax_podcasts'),
    path('ajax-courses/', ajax_courses, name='ajax_courses'),
    path('faq/', faq_list, name='faq'),
    path('guide/<slug:slug>/', guide_category, name='guide_category'),
    path('article/<slug:slug>/', guide_article, name='guide_article'),
    path('ticket/new/', create_ticket, name='create_ticket'),
    path('contact/', contact_support, name='contact_support'),
    # other urls...
]