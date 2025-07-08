from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('orders/', views.order_history, name='order_history'),
    path('income/', views.income_reports, name='income_reports'),
    path('tables/', views.table_management, name='table_management'),
    path('food/', views.food_management, name='food_management'),
    path('food/add-item/', views.add_food_item, name='add_food_item'),
    path('food/add-category/', views.add_food_category, name='add_food_category'),
    
    # AJAX endpoints
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('table/<int:table_id>/release/', views.release_table, name='release_table'),
    path('table/<int:table_id>/change-status/', views.change_table_status, name='change_table_status'),
    path('live-orders/', views.get_live_orders, name='get_live_orders'),
    path('generate-reports/', views.generate_reports, name='generate_reports'),
]