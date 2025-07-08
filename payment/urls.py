"""
URL patterns for payment app
"""
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('options/<int:order_id>/', views.payment_options, name='payment_options'),
    path('qr/<int:order_id>/', views.qr_payment, name='qr_payment'),
    path('counter/<int:order_id>/', views.counter_payment, name='counter_payment'),
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('success/<int:order_id>/', views.payment_success, name='payment_success'),
]