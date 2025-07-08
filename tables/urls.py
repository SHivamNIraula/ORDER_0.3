"""
URL patterns for tables app
"""
from django.urls import path
from . import views

app_name = 'tables'

urlpatterns = [
    path('', views.table_list, name='table_list'),
    path('select/<int:table_id>/', views.select_table, name='select_table'),
    path('release/', views.release_table, name='release_table'),
]