from django.urls import path
from . import views

app_name = 'purchase'

urlpatterns = [
    path('start/<str:content_type>/<int:object_id>/', views.start_purchase, name='start'),
    path('callback/<str:ref_id>/', views.payment_callback, name='callback'),
]