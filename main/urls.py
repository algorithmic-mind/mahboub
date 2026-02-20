# Add to urls.py in main app
from django.urls import path
from .views import main, ajax_books, ajax_podcasts, ajax_courses

app_name = 'main'
urlpatterns = [
    path('', main, name='main'),
    path('ajax-books/', ajax_books, name='ajax_books'),
    path('ajax-podcasts/', ajax_podcasts, name='ajax_podcasts'),
    path('ajax-courses/', ajax_courses, name='ajax_courses'),
    # other urls...
]