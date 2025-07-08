"""
URL patterns for food app
"""
from django.urls import path
from . import views

app_name = 'food'

urlpatterns = [
    path('', views.food_menu, name='food_menu'),
    path('category/<int:category_id>/', views.category_items, name='category_items'),
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:food_id>/', views.update_cart_quantity, name='update_cart_quantity'),
]