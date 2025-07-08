"""
URL configuration for restaurant_system project.
Restaurant Order Management System
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home_redirect(request):
    """Redirect root URL based on user authentication status"""
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_panel:dashboard')
        else:
            return redirect('tables:table_list')
    else:
        return redirect('authentication:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('auth/', include('authentication.urls')),
    path('tables/', include('tables.urls')),
    path('food/', include('food.urls')),
    path('orders/', include('orders.urls')),
    path('payment/', include('payment.urls')),
    path('admin-panel/', include('admin_panel.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)