from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from decimal import Decimal

from .models import AdminSettings, DailyReport, MonthlyReport
from orders.models import Order, OrderItem
from tables.models import Table
from food.models import FoodItem, FoodCategory
from payment.models import Payment
from .forms import TableForm, FoodItemForm, FoodCategoryForm

def is_staff_user(user):
    """Check if user is staff"""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_staff_user)
def admin_dashboard(request):
    """Main admin dashboard with overview statistics"""
    today = timezone.now().date()
    
    # Generate today's report
    daily_report = DailyReport.generate_daily_report(today)
    
    # Get recent orders
    recent_orders = Order.objects.select_related('customer', 'table').order_by('-created_at')[:10]
    
    # Get table status
    tables = Table.objects.all().order_by('table_number')
    available_tables = tables.filter(is_available=True).count()
    occupied_tables = tables.filter(is_available=False).count()
    
    # Get pending orders count
    pending_orders = Order.objects.filter(status__in=['pending', 'confirmed', 'preparing']).count()
    
    # Get current month stats
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_report = MonthlyReport.generate_monthly_report(current_year, current_month)
    
    context = {
        'daily_report': daily_report,
        'monthly_report': monthly_report,
        'recent_orders': recent_orders,
        'available_tables': available_tables,
        'occupied_tables': occupied_tables,
        'total_tables': tables.count(),
        'pending_orders': pending_orders,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_staff_user)
def order_history(request):
    """View all order history with filtering options"""
    orders = Order.objects.select_related('customer', 'table', 'payment').prefetch_related('items__food_item')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Search by customer or order ID
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(customer__username__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(id__icontains=search)
        )
    
    orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 25)  # Show 25 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'current_filters': {
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to,
            'search': search,
        }
    }
    
    return render(request, 'admin_panel/order_history.html', context)

@login_required
@user_passes_test(is_staff_user)
def income_reports(request):
    """View daily and monthly income reports"""
    # Get daily reports for current month
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    daily_reports = DailyReport.objects.filter(
        date__year=current_year,
        date__month=current_month
    ).order_by('-date')
    
    # Get monthly reports for current year
    monthly_reports = MonthlyReport.objects.filter(year=current_year).order_by('-month')
    
    # Calculate totals
    daily_total = daily_reports.aggregate(total=Sum('total_revenue'))['total'] or Decimal('0.00')
    yearly_total = monthly_reports.aggregate(total=Sum('total_revenue'))['total'] or Decimal('0.00')
    
    context = {
        'daily_reports': daily_reports,
        'monthly_reports': monthly_reports,
        'daily_total': daily_total,
        'yearly_total': yearly_total,
        'current_month': current_month,
        'current_year': current_year,
    }
    
    return render(request, 'admin_panel/income_reports.html', context)

@login_required
@user_passes_test(is_staff_user)
def table_management(request):
    """Manage restaurant tables"""
    tables = Table.objects.all().order_by('table_number')
    
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table created successfully!')
            return redirect('admin_panel:table_management')
    else:
        form = TableForm()
    
    context = {
        'tables': tables,
        'form': form,
    }
    
    return render(request, 'admin_panel/table_management.html', context)

@login_required
@user_passes_test(is_staff_user)
def food_management(request):
    """Manage food items and categories"""
    categories = FoodCategory.objects.prefetch_related('items').all()
    food_items = FoodItem.objects.select_related('category').order_by('category', 'name')
    
    context = {
        'categories': categories,
        'food_items': food_items,
    }
    
    return render(request, 'admin_panel/food_management.html', context)

@login_required
@user_passes_test(is_staff_user)
def add_food_item(request):
    """Add new food item"""
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Food item added successfully!')
            return redirect('admin_panel:food_management')
    else:
        form = FoodItemForm()
    
    context = {'form': form}
    return render(request, 'admin_panel/add_food_item.html', context)

@login_required
@user_passes_test(is_staff_user)
def add_food_category(request):
    """Add new food category"""
    if request.method == 'POST':
        form = FoodCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Food category added successfully!')
            return redirect('admin_panel:food_management')
    else:
        form = FoodCategoryForm()
    
    context = {'form': form}
    return render(request, 'admin_panel/add_food_category.html', context)

@login_required
@user_passes_test(is_staff_user)
@require_POST
def update_order_status(request, order_id):
    """Update order status via AJAX"""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    
    if new_status in dict(Order.ORDER_STATUS_CHOICES):
        order.status = new_status
        if new_status in ['delivered', 'paid']:
            order.completed_at = timezone.now()
        order.save()
        
        # Broadcast to admin panel
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'admin_orders',
            {
                'type': 'order_update',
                'order': {
                    'id': order.id,
                    'customer': order.customer.username,
                    'table_number': order.table.table_number,
                    'status': order.status,
                    'status_display': order.get_status_display(),
                    'total_amount': str(order.total_amount),
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
            }
        )
        
        # Broadcast to customer
        async_to_sync(channel_layer.group_send)(
            f'customer_orders_{order.customer.id}',
            {
                'type': 'order_status_update',
                'order': {
                    'id': order.id,
                    'status': order.status,
                    'status_display': order.get_status_display(),
                    'total_amount': str(order.total_amount),
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'table_number': order.table.table_number,
                    'completed_at': order.completed_at.strftime('%Y-%m-%d %H:%M:%S') if order.completed_at else None,
                }
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Order status updated to {order.get_status_display()}'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid status'
    })

@login_required
@user_passes_test(is_staff_user)
@require_POST
def release_table(request, table_id):
    """Release a table via AJAX"""
    table = get_object_or_404(Table, id=table_id)
    table.release_table()
    
    return JsonResponse({
        'success': True,
        'message': f'Table {table.table_number} has been released'
    })

@login_required
@user_passes_test(is_staff_user)
@require_POST
def change_table_status(request, table_id):
    """Change table status between available and occupied via AJAX"""
    table = get_object_or_404(Table, id=table_id)
    
    if table.is_available:
        # Mark as occupied
        table.is_available = False
        table.reserved_at = timezone.now()
        # Don't assign a user for manual status changes
        status_message = f'Table {table.table_number} marked as occupied'
    else:
        # Mark as available
        table.release_table()
        status_message = f'Table {table.table_number} marked as available'
    
    table.save()
    
    return JsonResponse({
        'success': True,
        'message': status_message,
        'new_status': 'Available' if table.is_available else 'Occupied',
        'is_available': table.is_available
    })

@login_required
@user_passes_test(is_staff_user)
def get_live_orders(request):
    """Get live orders data for real-time updates"""
    orders = Order.objects.filter(
        status__in=['pending', 'confirmed', 'preparing']
    ).select_related('customer', 'table').order_by('-created_at')[:20]
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'customer': order.customer.username,
            'table': order.table.table_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'total_amount': str(order.total_amount),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'orders': orders_data})

@login_required
@user_passes_test(is_staff_user)
def generate_reports(request):
    """Generate daily and monthly reports"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        
        if report_type == 'daily':
            date_str = request.POST.get('date')
            if date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                DailyReport.generate_daily_report(date)
                messages.success(request, f'Daily report generated for {date}')
        
        elif report_type == 'monthly':
            year = int(request.POST.get('year'))
            month = int(request.POST.get('month'))
            MonthlyReport.generate_monthly_report(year, month)
            messages.success(request, f'Monthly report generated for {month}/{year}')
    
    return redirect('admin_panel:income_reports')
