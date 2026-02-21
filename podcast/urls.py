from django.urls import re_path
from . import views

app_name = 'podcasts'

urlpatterns = [
    re_path(r'^$',                               views.podcasts_list,        name='podcasts_list'),
    re_path(r'^category/(?P<slug>[^/]+)/$',      views.podcasts_by_category, name='podcasts_by_category'),
    re_path(r'^(?P<slug>[^/]+)/$',               views.podcast_detail,       name='podcast_detail'),
]