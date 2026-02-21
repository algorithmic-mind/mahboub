from django.urls import re_path, path
from . import views

app_name = 'courses'

urlpatterns = [
    re_path(r'^$',                                    views.courses_list,        name='courses_list'),
    re_path(r'^category/(?P<slug>[^/]+)/$',           views.courses_by_category, name='courses_by_category'),
    path('<slug:course_slug>/lesson/<int:lesson_id>/', views.lesson_view,         name='lesson_view'),
    re_path(r'^(?P<slug>[^/]+)/$',                    views.course_detail,        name='course_detail'),
]