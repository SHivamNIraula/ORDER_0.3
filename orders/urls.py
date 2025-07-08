"""
URL patterns for orders app
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.create_order, name='create_order'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('cart/', views.view_cart, name='view_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
]